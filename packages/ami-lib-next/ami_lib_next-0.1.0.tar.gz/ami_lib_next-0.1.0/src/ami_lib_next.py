# -*- coding: utf-8 -*-
"""
update time: 2025-09-17

ami_lib 优化重构（可直接替换）
- 仅创建 logger；不配置 basicConfig
- 统一请求发送入口：加密/非加密均可；headers/seed 处理清晰
- 修复 pre_headers 未定义、data_cipher 在非加密分支使用等逻辑问题
- 更健壮的响应解析：优先 JSON，不行回退 text；加密时自动走 handle_response
- 安全修正：移除明文打印账号；Authorization 为空时不下发该头
- 验证码计算鲁棒性：修正 resize 逻辑与时间戳毫秒精度
- 轻量重试：对网络异常做指数退避
依赖：requests, numpy, opencv-python, ami_crypto（或 ami_crypto_next 中的 AmiCrypto）
"""
from __future__ import annotations

import os
import json
import time
import base64
import logging
import traceback
from typing import Optional, Dict, Any

import requests
import numpy as np
import cv2

from ami_crypto_next import AmiCrypto  # 若模块名为 ami_crypto，请自行替换

logger = logging.getLogger(__name__)


def _millis() -> int:
    # 保证毫秒精度：int(time.time()*1000)
    return int(time.time() * 1000)


def _calculate_image_move(captcha_structure: Dict[str, Any]) -> Optional[int]:
    """计算验证码滑块移动距离（返回 x 像素）。"""
    try:
        rep = captcha_structure.get("repData", {})
        bg_b64 = rep.get("originalImageBase64")
        sl_b64 = rep.get("jigsawImageBase64")
        if not bg_b64 or not sl_b64:
            logger.warning("验证码图片缺失 repData.originalImageBase64 / jigsawImageBase64")
            return None

        bg = cv2.imdecode(np.frombuffer(base64.b64decode(bg_b64), np.uint8), cv2.IMREAD_COLOR)
        sl = cv2.imdecode(np.frombuffer(base64.b64decode(sl_b64), np.uint8), cv2.IMREAD_COLOR)
        if bg is None or sl is None:
            logger.warning("验证码图片解码失败")
            return None

        # 统一宽度 380px，保持纵横比
        k = 380.0 / float(bg.shape[1])
        new_w = 380
        new_h = int(round(bg.shape[0] * k))
        bg = cv2.resize(bg, (new_w, new_h), interpolation=cv2.INTER_AREA)
        sl = cv2.resize(sl, (int(round(sl.shape[1] * k)), int(round(sl.shape[0] * k))), interpolation=cv2.INTER_AREA)

        bg_gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        sl_gray = cv2.cvtColor(sl, cv2.COLOR_BGR2GRAY)
        # 二值化 + 模板模糊，提升匹配鲁棒性
        _, bg_thresh = cv2.threshold(bg_gray, 254, 255, cv2.THRESH_BINARY)
        sl_blur = cv2.GaussianBlur(sl_gray, (5, 5), 0)

        result = cv2.matchTemplate(bg_thresh, sl_blur, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        x, _ = max_loc
        logger.debug("captcha move x=%d", x)
        return int(x)
    except Exception as e:
        logger.error("验证码计算失败: %s", e)
        logger.debug(traceback.format_exc())
        return None


class AmiBase:
    def __init__(
        self,
        auth_token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        encrypt: bool = False,
        host: str = "http://20.58.101.34:31051",
        timeout_sec: int = 30,
        max_retries: int = 2,
    ) -> None:
        self.host = host.rstrip("/")
        self.auth_token = auth_token or os.getenv("DIAN_CAI_AUTH_TOKEN")
        self.username = username
        self.password = password
        self.encrypt = encrypt
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries

        # headers：Authorization 仅在 token 存在时下发
        self.headers: Dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0",
            "Content-Type": "application/json",
        }
        self._sync_auth_header()

        # 加密客户端（默认 SM4 content=02）
        self.ami_client = AmiCrypto(enc_type="02", content="02")

        # 运行态
        self.user: Optional[Dict[str, Any]] = None

        # 子模块
        self.User = self.User(self)
        self.SideBar = self.SideBar(self)
        self.Bdq = self.Bdq(self)
        self.GfBaseInfoDetails = self.GfBaseInfoDetails(self)

    # ---------- 内部工具 ----------
    def _sync_auth_header(self) -> None:
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
        else:
            self.headers.pop("Authorization", None)

    def _request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.request(method, url, timeout=self.timeout_sec, **kwargs)
                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                last_exc = e
                logger.warning("HTTP %s %s 失败（第 %d 次）: %s", method, url, attempt + 1, e)
                if attempt < self.max_retries:
                    time.sleep(min(2 ** attempt, 4))  # 指数退避
                else:
                    raise
        assert False, last_exc  # 理论到不了

    # ---------- 统一请求入口 ----------
    def send_request(
        self,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Optional[Dict[str, Any]]:
        """发送 HTTP 请求，自动处理加解密与响应解析。
        返回 dict；失败返回 None。
        """
        url = path if path.startswith("http") else f"{self.host}{path}"
        payload = payload or {}
        params = params or {}

        logger.debug("发送请求 -> %s %s payload=%s params=%s encrypt=%s", method, url, payload, params, self.encrypt)

        try:
            if self.encrypt:
                # 加密报文（content=02：只加 data）
                pre_headers, data_cipher, params_cipher, _ = self.ami_client.build_request(
                    headers=self.headers, data=payload, params=params
                )
                # 加密场景以纯文本密文作为请求体
                resp = self._request_with_retry(method, url, headers=pre_headers, data=data_cipher)
                # 优先尝试 JSON
                try:
                    body: Any = resp.json()
                except json.JSONDecodeError:
                    body = resp.text
                # 解密响应
                result = self.ami_client.handle_response(resp_headers=resp.headers, full_body=body)
                logger.debug("请求成功 -> 解密响应: %s", result)
                return result if isinstance(result, dict) else json.loads(result)
            else:
                # 非加密：直接发 JSON
                resp = self._request_with_retry(method, url, headers=self.headers, json=payload, params=params)
                try:
                    result = resp.json()
                except json.JSONDecodeError:
                    # 回退 text
                    txt = resp.text
                    logger.debug("非加密响应非 JSON，原文返回 text 长度=%d", len(txt))
                    return {"raw": txt}
                logger.debug("请求成功 -> 响应: %s", result)
                return result
        except requests.exceptions.RequestException as e:
            logger.error("请求失败: %s", e)
        except Exception as e:
            logger.error("未知错误: %s", e)
            logger.debug(traceback.format_exc())
        return None

    # ====================== 子模块 ======================
    class User:
        def __init__(self, base_instance: "AmiBase") -> None:
            self.base = base_instance

        def login(self) -> bool:
            """用户名密码登录；需要 base.encrypt=True 才会走加密链路。"""
            if not self.base.username or not self.base.password:
                logger.error("必须提供用户名和密码。")
                return False

            # 账号加密（SM2 公钥加密）
            try:
                username_enc = self.base.ami_client.legacy.sm2_encrypt(content=self.base.username)
                password_enc = self.base.ami_client.legacy.sm2_encrypt(content=self.base.password)
                captcha_verification = self._handle_captcha()
                path = "/ami/ma01-00-101/auth/login"
                payload = {
                    "clientId": "test",
                    "clientSecret": "test",
                    "grantType": "password",
                    "username": username_enc,
                    "pd": password_enc,
                    "captchaVerification": captcha_verification,
                }
                resp = self.base.send_request(path, payload)
                logger.debug("login resp: %s", resp)
            except Exception:
                logger.error("登录加密或请求异常")
                logger.debug(traceback.format_exc())
                return False

            if resp and resp.get("code") == 200:
                self.base.auth_token = resp.get("data", {}).get("accessToken")
                self.base._sync_auth_header()
                self._get_user()
                logger.info("登录成功")
                return True
            logger.warning("登录失败: %s", resp)
            return False

        def _get_user(self) -> Optional[Dict[str, Any]]:
            if not self.base.auth_token:
                logger.error("未登录。")
                return None
            path = "/ami/ma01-00-101/user/getUser"
            resp = self.base.send_request(path, None)
            if resp and resp.get("code") == 200:
                self.base.user = resp.get("data", {})
                logger.debug("用户信息获取成功")
                return self.base.user
            logger.warning("用户信息获取失败: %s", resp)
            return None

        def _handle_captcha(self) -> Optional[str]:
            path = "/ami/ma01-00-101/captcha/get"
            ts = _millis()
            payload = {"captchaType": "blockPuzzle", "clientUid": ts, "ts": ts}
            result = self.base.send_request(path, payload)
            if not result or "repData" not in result:
                logger.error("获取验证码失败")
                return None

            move_distance = _calculate_image_move(result)
            return self._check_captcha(result, move_distance, 380)

        def _check_captcha(self, captcha_structure: Dict[str, Any], move_block_left: Optional[int], img_width: int) -> Optional[str]:
            if move_block_left is None:
                return None
            x = (310.0 * float(move_block_left)) / float(img_width)
            y = 5
            rep = captcha_structure.get("repData", {})
            secret_key = rep.get("secretKey")
            token = rep.get("token")
            point_json = json.dumps({"x": x, "y": y}, separators=(",", ":"))
            point_json_encrypted = self.base.ami_client.legacy.aes_encrypt(data=point_json, _skey=secret_key) if secret_key else point_json
            path = "/ami/ma01-00-101/captcha/check"
            payload = {"captchaType": "blockPuzzle", "pointJson": point_json_encrypted, "token": token}
            result = self.base.send_request(path, payload)
            logger.debug("check captcha resp: %s", result)
            if not result or result.get("repCode") != "0000":
                logger.warning("验证码核验失败！")
                return None
            return self._finalize_captcha(captcha_structure, point_json)

        def _finalize_captcha(self, captcha_structure: Dict[str, Any], point_json: str) -> Optional[str]:
            try:
                rep = captcha_structure.get("repData", {})
                secret_key = rep.get("secretKey")
                token = rep.get("token")
                if secret_key:
                    return self.base.ami_client.legacy.aes_encrypt(data=f"{token}---{point_json}", _skey=secret_key)
                return f"{token}---{point_json}"
            except Exception as e:
                logger.error("验证码最终处理异常: %s", e)
                logger.debug(traceback.format_exc())
                return None

    class SideBar:
        def __init__(self, base_instance: "AmiBase") -> None:
            self.base = base_instance

        def search_cust(self, is_user: bool = True, cust_no: Optional[list] = None, page_index: int = 1, page_size: int = 9999):
            try:
                payload = {
                    "filter": {"mgtOrgCode": (self.base.user or {}).get("mgtOrgCode"), "custNo": cust_no},
                    "pageIndex": page_index,
                    "pageSize": page_size,
                }
                path = "/ami/ma01-00-101/user/queryElecConsCustNew" if is_user else "/ami/ma01-00-101/user/queryAllGenerator"
                resp = self.base.send_request(path, payload)
                if resp and resp.get("code") == 200:
                    logger.debug("获取数据成功")
                    return resp.get("data", {}).get("list")
                logger.warning("获取数据失败: %s", resp)
                return None
            except Exception as e:
                logger.error("search_cust 失败: %s", e)
                logger.debug(traceback.format_exc())
                return None

    class Bdq:
        def __init__(self, base_instance: "AmiBase") -> None:
            self.base = base_instance

        def query_main_info(
            self,
            checked: bool = False,
            s_date: str = "",
            e_date: str = "",
            mr_sect_no: str = "",
            asset_no: str = "",
            user_flag: Optional[list] = None,
            is_zero: str = "",
            is_gf: str = "",
            data_state: str = "",
            left_nav: str = "",
            obj_id: str = "",
            page_index: int = 1,
            page_size: int = 9999,
        ) -> Optional[Dict[str, Any]]:
            try:
                payload = {
                    "filter": {
                        "checked": checked,
                        "sDate": s_date,
                        "eDate": e_date,
                        "mrSectNo": mr_sect_no,
                        "assetNo": asset_no,
                        "userFlag": (user_flag or []),
                        "isZero": is_zero,
                        "isGf": is_gf,
                        "dataState": data_state,
                        "leftNav": left_nav,
                        "objId": obj_id,
                        "userCorpNo": (self.base.user or {}).get("mgtOrgCode"),
                    },
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "sorts": [],
                }
                return self.base.send_request("/ami/ma41-02-505/bdq/queryMainInfo", payload)
            except Exception as e:
                logger.error("query_main_info 失败: %s", e)
                logger.debug(traceback.format_exc())
                return None

        def query_curve_data(
            self,
            table_name: str = "",
            s_date: str = "",
            e_date: str = "",
            curr_type: Optional[list] = None,
            side_type: str = "01",
            mped_id: str = "",
            tab_flag: str = "",
            ct: str = "1",
            pt: str = "1",
            compRto: str = "1",
            is_yc: bool = True,
        ) -> Optional[Dict[str, Any]]:
            try:
                payload = {
                    "tableName": table_name,
                    "sDate": s_date,
                    "eDate": e_date,
                    "currType": (curr_type or []),
                    "sideType": side_type,
                    "mpedId": mped_id,
                    "tabFlag": tab_flag,
                    "compRto": compRto,
                    "ct": ct,
                    "pt": pt,
                    "isYc": "00" if is_yc else "01",
                }
                resp = self.base.send_request("/ami/ma41-02-505/bdq/queryCurveData", payload)
                if resp and resp.get("code") == 200:
                    logger.debug("获取数据成功")
                    return resp.get("data", {})
                logger.warning("获取数据失败: %s", resp)
                return None
            except Exception as e:
                logger.error("query_curve_data 失败: %s", e)
                logger.debug(traceback.format_exc())
                return None

    class GfBaseInfoDetails:
        def __init__(self, base_instance: "AmiBase") -> None:
            self.base = base_instance

        def get_basic_info_detail(
            self,
            abso_mode: str = "",
            asset_no: str = "",
            cons_no: str = "",
            controll_code: str = "",
            cp_no: str = "",
            data_date: str = "",
            is_hplc: str = "",
            is_pr: str = "",
            mp_use: str = "",
            org_no: str = "",
            tg_name: str = "",
            tg_no: str = "",
            tmnl_addr: str = "",
            tmnl_area_code: str = "",
            tmnl_factor: str = "",
            tmnl_statute: str = "",
            wiring_mode: str = "",
            page_index: int = 1,
            page_size: int = 9999,
        ) -> Optional[Dict[str, Any]]:
            try:
                payload = {
                    "filter": {
                        "absoMode": abso_mode,
                        "assetNo": asset_no,
                        "consNo": cons_no,
                        "controllCode": controll_code,
                        "cpNo": cp_no,
                        "dataDate": data_date,
                        "isHplc": is_hplc,
                        "isPr": is_pr,
                        "mpUse": mp_use,
                        "orgNo": org_no,
                        "tgName": tg_name,
                        "tgNo": tg_no,
                        "tmnlAddr": tmnl_addr,
                        "tmnlAreaCode": tmnl_area_code,
                        "tmnlFactor": tmnl_factor,
                        "tmnlStatute": tmnl_statute,
                        "wiringMode": wiring_mode,
                    },
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "sorts": [],
                }
                return self.base.send_request("/ami/ma41-03-502/pcStatAnalysis/getBasicInfoDetail", payload)
            except Exception as e:
                logger.error("get_basic_info_detail 失败: %s", e)
                logger.debug(traceback.format_exc())
                return None


def is_break(data: str) -> bool:
    """检查返回数据是否表示操作中断。输入既可为 JSON 文本也可为 dict。"""
    try:
        obj = json.loads(data) if isinstance(data, str) else data
        logger.info("code: %s, 错误信息：%s", obj.get("code", "未知"), obj.get("message", "未知错误"))
        return True
    except Exception as e:
        logger.error("JSON 解析失败: %s", e)
        return False
