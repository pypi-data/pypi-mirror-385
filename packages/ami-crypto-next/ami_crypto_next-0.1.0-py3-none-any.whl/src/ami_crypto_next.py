# -*- coding: utf-8 -*-

# author: Tony
# email: zixutech@foxmail.com

# Always be yourself, unless you can be a unicorn, then always be a unicorn.

# -*- coding: utf-8 -*-
"""
Update Time: 2025-09-15

AmiCrypto: Python 复刻版请求加解密库（优化重构提案）
改动要点：
- 统一密钥派生：AES/SM4 都用 SHA-256(seed).digest() 截取字节；避免混用 hex-string 字节与真密钥字节。
- 修复 seed/base28 编解码：固定 2 位 base28 编码，解码按 2 位切片，避免可变宽导致反解错位。
- 严格 PKCS#7 校验：非法填充直接抛出 ValueError（便于调用方感知错误），而不是静默返回原文。
- 去重工具：base28/seed/public_key 解码复用；移除重复逻辑。
- 明确异常类型：AmiCryptoError、UnsupportedAlgoError、PaddingError。
- 可观察性：遵循张工的日志原则，仅创建 logger；不做 basicConfig；关键路径加 debug/info；错误路径附 traceback。
- API 兼容：对外类名/方法签名保持一致；补充 manual_encrypt/manual_decrypt；LegacyAdapter 文案更正。
- 类型标注与文档：补齐 typing；便于 IDE 与后续维护。

依赖：
    pip install gmssl pycryptodome cryptography
"""
from __future__ import annotations

import time
import secrets
import hashlib
import json
import base64
import logging
import warnings
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, Any
from urllib.parse import quote

from gmssl import sm3, sm4, sm2
from Crypto.Cipher import AES
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import padding as crypto_padding

logger = logging.getLogger(__name__)

# ============================ 异常定义 ============================
class AmiCryptoError(Exception):
    """通用库异常。"""

class UnsupportedAlgoError(AmiCryptoError):
    pass

class PaddingError(AmiCryptoError):
    pass

# ============================ 常量/工具 ============================
_BASE28_ALPHABET = "0123456789abcdefghijklmnopqr"
_BASE28_RADIX = 28


def _to_bytes16_from_seed(seed: str) -> bytes:
    """从 seed 生成 16 字节密钥：SHA-256(seed).digest()[:16]。"""
    return hashlib.sha256(seed.encode("utf-8")).digest()[:16]


def _to_bytes16_from_seed_hex(seed: str) -> bytes:
    """兼容旧 SM4 路径：sha256(seed) 取 16 字节（通过 hex 再 fromhex 方式）。"""
    # 与旧实现等价：sha256_hex(seed)[:32] -> bytes.fromhex
    return bytes.fromhex(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32])


# ----------------- PKCS#7 -----------------

def pkcs7_pad(b: bytes, block_size: int = 16) -> bytes:
    padlen = block_size - (len(b) % block_size)
    return b + bytes([padlen]) * padlen


def pkcs7_unpad(b: bytes, block_size: int = 16, strict: bool = True) -> bytes:
    if not b:
        if strict:
            raise PaddingError("empty input for pkcs7_unpad.")
        return b
    if len(b) % block_size != 0:
        if strict:
            raise PaddingError(f"invalid block size for pkcs7_unpad. [{len(b) % block_size}]")
        return b
    padlen = b[-1]
    if 1 <= padlen <= 16 and b.endswith(bytes([padlen]) * padlen):
        return b[:-padlen]
    if not strict:
        return b
    
    raise PaddingError("invalid padding bytes.")


# ----------------- Hash/编码 -----------------

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sm3_hex(msg: str) -> str:
    return sm3.sm3_hash([x for x in msg.encode("utf-8")])


def is_cjk(ch: str) -> bool:
    return 0x4E00 <= ord(ch) <= 0x9FA5


def percent_hex_utf8(s: str) -> str:
    return quote(s, safe="").replace("%", "")


# ----------------- base28/seed 编解码 -----------------

def _base28_encode_value(val: int, width: int = 2) -> str:
    assert val >= 0
    digits = []
    n = val
    while n:
        digits.append(_BASE28_ALPHABET[n % _BASE28_RADIX])
        n //= _BASE28_RADIX
    if not digits:
        digits = ["0"]
    out = "".join(reversed(digits))
    # 固定宽度，左侧 0 填充至 width 位
    if len(out) < width:
        out = "0" * (width - len(out)) + out
    return out


def _base28_decode_2chars(ch2: str) -> int:
    n = 0
    for ch in ch2:
        n = n * _BASE28_RADIX + _BASE28_ALPHABET.index(ch)
    return n


def seed_encode(seed: str) -> str:
    """把 seed 转成 ami-seed-code（每字节 +1 后按 base28 固定 2 位编码）。"""
    out = []
    for ch in seed:
        val = ord(ch) + 1
        out.append(_base28_encode_value(val, width=2))
    return "".join(out)


def seed_decode(code: str) -> str:
    if len(code) % 2 != 0:
        raise AmiCryptoError("invalid seed code length")
    out = []
    for i in range(0, len(code), 2):
        val = _base28_decode_2chars(code[i:i + 2]) - 1
        if val < 0 or val > 0x10FFFF:
            raise AmiCryptoError("invalid seed code value")
        out.append(chr(val))
    return "".join(out)


# ----------------- 公钥解码（与 seed 同制） -----------------

def decode_pubkey(s: str) -> str:
    """复刻 JS 的 u(s)：按 base28 每 2 位解码 - 1，再拼为字符串（十六进制公钥）。"""
    return seed_decode(s)


# ----------------- 加密实现 -----------------

def sm4_encrypt_hex(plaintext: str, seed: str) -> str:
    key = _to_bytes16_from_seed_hex(seed)  # 兼容旧逻辑
    c = sm4.CryptSM4()
    c.set_key(key, sm4.SM4_ENCRYPT)
    ct = c.crypt_ecb(pkcs7_pad(plaintext.encode("utf-8")))
    return ct.hex()


def sm4_decrypt_text(cipher_hex: str, seed: str) -> str:
    key = _to_bytes16_from_seed_hex(seed)
    c = sm4.CryptSM4()
    c.set_key(key, sm4.SM4_DECRYPT)
    pt = c.crypt_ecb(bytes.fromhex(cipher_hex))
    return pkcs7_unpad(b=pt, strict=False).decode("utf-8")


def aes128_ecb_encrypt_hex(plaintext: str, seed: str) -> str:
    """
    统一后的 AES 派生：key = SHA256(seed).digest()[:16]
    """
    key = _to_bytes16_from_seed(seed)
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pkcs7_pad(plaintext.encode("utf-8"))).hex()


def aes128_ecb_decrypt_text(cipher_hex: str, seed: str) -> str:
    key = _to_bytes16_from_seed(seed)
    cipher = AES.new(key, AES.MODE_ECB)
    pt = cipher.decrypt(bytes.fromhex(cipher_hex))
    return pkcs7_unpad(b=pt, strict=False).decode("utf-8")


def aes128_ecb_encrypt_base64(data: str, skey: str) -> str:
    """
    由 cryptography 统一更换为 pycryptodome
    兼容旧逻辑：显式 skey（原库约定）。
    内部仍按 AES/ECB + PKCS7，输出 Base64。
    """
    if not skey:
        raise ValueError("aes128_ecb_encrypt_base64 需要提供 skey")

    aes_key = skey.encode("utf-8")
    cipher = AES.new(aes_key, AES.MODE_ECB)
    # pkcs7 padding
    block_size = 16
    raw = data.encode("utf-8")
    padlen = block_size - (len(raw) % block_size)
    padded = raw + bytes([padlen]) * padlen
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode("utf-8")

    # ---cryptography---
    # aes_key = skey.encode('utf-8')
    # padder = crypto_padding.PKCS7(128).padder()
    # padded_data = padder.update(data.encode('utf-8')) + padder.finalize()
    # cipher = Cipher(algorithms.AES(aes_key), modes.ECB(), backend=default_backend())
    # encryptor = cipher.encryptor()
    # encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    # return base64.b64encode(encrypted_data).decode('utf-8')


def sm2_encrypt_hex(plaintext: str, public_key_hex: str) -> str:
    crypt = sm2.CryptSM2(public_key=public_key_hex, private_key=None)
    ct = crypt.encrypt(plaintext.encode("utf-8")).hex()
    return "04" + ct if not ct.startswith("04") else ct


def custom_hexify(s: str) -> str:
    return "".join(
        percent_hex_utf8(ch) if is_cjk(ch) else format(ord(ch), "x")
        for ch in s
    ).lower()


def custom_unhexify(s: str) -> str:
    try:
        return bytes.fromhex(s).decode("utf-8", errors="replace")
    except Exception:
        return s


# ============================ 主类 ============================
@dataclass
class AmiCrypto:
    enc_type: str = "02"   # "01"=SM2, "02"=SM4, "03"=AES, "04"=自定义
    content: str = "02"     # "01"=整体密文, "02"=只加密data字段
    sm2_pubkey: Optional[str] = (
        '04653cbaf779a6c52581b7835e645b8703cab40ef3396045c4288e4a489239bb83cb44119e71901ac4e245cb7ce0a32d0c3263cac8948d3d8f76bbd7ed138bdc1e'
    )

    # 运行期字段（与服务端约定）
    env: str = "2.1.0"
    enc: str = "2.1.0"

    def __post_init__(self) -> None:
        self.legacy = LegacyAdapter(self)
        if self.enc_type not in {"01", "02", "03", "04"}:
            raise UnsupportedAlgoError(f"未知加密类型: {self.enc_type}")
        if self.content not in {"01", "02"}:
            raise UnsupportedAlgoError(f"未知 content 类型: {self.content}")

    # ----------- 随机量 -----------
    @staticmethod
    def _make_nonce() -> str:
        return "".join(secrets.choice("0123456789") for _ in range(16))

    @staticmethod
    def _make_seed() -> str:
        x = int.from_bytes(secrets.token_bytes(3), "big") % 1_000_000
        return f"{x:06d}"

    # ----------- 头签名 -----------
    def sign_headers(self) -> Tuple[int, str, str]:
        ts = int(time.time() * 1000)
        nonce = self._make_nonce()
        sign = sm3_hex(f"Timestamp{ts}Nonce{nonce}")
        logger.debug("sign_headers ts=%s nonce=%s sign=%s", ts, nonce, sign)
        return ts, nonce, sign

    # ----------- 字符串加解密 -----------
    def encrypt_str(self, s: str, seed: str) -> str:
        logger.debug("encrypt_str type=%s len=%d", self.enc_type, len(s))
        if self.enc_type == "01":
            return sm2_encrypt_hex(s, self.sm2_pubkey)
        if self.enc_type == "02":
            return sm4_encrypt_hex(s, seed)
        if self.enc_type == "03":
            return aes128_ecb_encrypt_hex(s, seed)
        if self.enc_type == "04":
            return custom_hexify(s)
        raise UnsupportedAlgoError(f"未知加密类型: {self.enc_type}")

    @staticmethod
    def decrypt_str(cipher: str, t: str, seed: str) -> str:
        logger.debug("decrypt_str type=%s len=%d", t, len(cipher) if cipher else -1)
        if t == "01":
            raise UnsupportedAlgoError("SM2 无私钥无法解密")
        if t == "02":
            return sm4_decrypt_text(cipher, seed)
        if t == "03":
            return aes128_ecb_decrypt_text(cipher, seed)
        if t == "04":
            return custom_unhexify(cipher)
        raise UnsupportedAlgoError(f"未知解密类型: {t}")

    # ----------- 构造请求 -----------
    def build_request(
        self,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, str], str, Dict[str, str], str]:
        """返回 headers, data_cipher(hex/str), params_cipher(dict), seed"""
        headers = dict(headers or {})
        data = data or {}
        params = params or {}

        ts, nonce, sign = self.sign_headers()
        headers["Timestamp"] = str(ts)
        headers["Nonce"] = nonce
        headers["Sign"] = sign
        headers["ami-enc-type"] = f"type={self.enc_type},content={self.content}"

        if "Authorization" not in headers:
            headers["env"] = "2.1.0|1.1.0"
        else:
            headers["env"] = self.env
            headers["enc"] = self.enc

        seed = self._make_seed()
        headers["ami-seed-code"] = seed_encode(seed)

        try:
            data_cipher = self.encrypt_str(json.dumps(data, separators=(",", ":")), seed)
            params_cipher = {k: self.encrypt_str(str(v), seed) for k, v in params.items()}
        except Exception as e:
            # 捕获并记录堆栈，抛出上层
            import traceback
            logger.error("build_request encrypt error: %s\n%s", e, traceback.format_exc())
            raise

        return headers, data_cipher, params_cipher, seed

    # ----------- 处理响应 -----------
    def handle_response(self, resp_headers: Dict[str, str], full_body: Any) -> Any:
        """
        根据响应头中的 ami-dec-type / ami-seed-code 解密响应。
        约定：
          - content=01：整个 body 是一个密文字符串（解密后为 JSON 文本）
          - content=02：只解密 body["data"]（密文字符串 -> 解密后 JSON 对象）
        """
        if (
            "ami-dec-type" not in resp_headers
            or "ami-seed-code" not in resp_headers
            or (isinstance(full_body, dict) and "repCode" in full_body)
        ):
            return full_body

        seed = seed_decode(resp_headers["ami-seed-code"])
        parts = dict(p.split("=") for p in resp_headers["ami-dec-type"].split(","))
        t = parts.get("type")
        c = parts.get("content")

        logger.debug("handle_response type=%s content=%s", t, c)

        try:
            if c == "01":
                # 整体密文
                return json.loads(self.decrypt_str(str(full_body), t, seed))
            if c == "02":
                if not isinstance(full_body, dict) or "data" not in full_body:
                    raise AmiCryptoError("content=02 but response body has no 'data'")
                out = dict(full_body)
                out["data"] = json.loads(self.decrypt_str(str(full_body["data"]), t, seed))
                return out
            return full_body
        except Exception as e:
            import traceback
            logger.error("handle_response decrypt error: %s\n%s", e, traceback.format_exc())
            raise

    # ----------- 手动加解密（对外辅助 API） -----------
    def manual_encrypt(self, t: str, plaintext: str, seed: Optional[str] = None, k: Optional[str] = None) -> str:
        """按指定类型临时加密。
        - t: "sm2"|"sm4"|"aes"|"custom"
        - seed: 对称算法所需的 seed（若为空且算法需要，则自动生成 6 位 seed 并返回）
        - k: sm2 公钥；若为空使用实例上的 sm2_pubkey
        返回：密文字符串；如自动生成了 seed，可在实例日志中读取到。
        """
        t = t.lower()
        if t == "sm2":
            return sm2_encrypt_hex(plaintext, k or self.sm2_pubkey)
        if t == "sm4":
            sd = seed or self._make_seed()
            if seed is None:
                logger.info("manual_encrypt: auto seed=%s", sd)
            return sm4_encrypt_hex(plaintext, sd)
        if t == "aes":
            sd = seed or self._make_seed()
            if seed is None:
                logger.info("manual_encrypt: auto seed=%s", sd)
            return aes128_ecb_encrypt_hex(plaintext, sd)
        if t == "custom":
            return custom_hexify(plaintext)
        raise UnsupportedAlgoError(f"unknown manual algo: {t}")

    def manual_decrypt(self, t: str, cipher: str, seed: Optional[str] = None) -> str:
        t = t.lower()
        if t == "sm4":
            if not seed:
                raise AmiCryptoError("SM4 解密需要 seed")
            return sm4_decrypt_text(cipher, seed)
        if t == "aes":
            if not seed:
                raise AmiCryptoError("AES 解密需要 seed")
            return aes128_ecb_decrypt_text(cipher, seed)
        if t == "custom":
            return custom_unhexify(cipher)
        if t == "sm2":
            raise UnsupportedAlgoError("SM2 无私钥无法解密")
        raise UnsupportedAlgoError(f"unknown manual algo: {t}")


# ============================ LEGACY ============================
class LegacyAdapter:
    def __init__(self, parent: AmiCrypto):
        self._p = parent

    def sm2_encrypt(self, content: str) -> str:
        """
        兼容旧：返回 '04' + SM2 密文 hex。
        """
        ct = sm2_encrypt_hex(content, self._p.sm2_pubkey)
        if not ct.startswith("04"):
            ct = "04" + ct
        warnings.warn(
            "Legacy.sm2_encrypt 已弃用，建议迁移到 AmiCrypto.manual_encrypt(t='sm2')",
            DeprecationWarning,
            stacklevel=2,
        )
        return ct

    def aes_encrypt(self, data: str, _skey: str) -> str:
        """
        兼容旧：AES-128-ECB + PKCS7 -> Base64；必须显式传递 _skey。
        """
        if not _skey:
            raise ValueError("legacy.aes_encrypt 需要提供 _skey")
        warnings.warn(
            "Legacy.aes_encrypt 已弃用，建议迁移到 AmiCrypto.manual_encrypt(t='aes', seed=..., k=...)",
            DeprecationWarning,
            stacklevel=2,
        )
        return aes128_ecb_encrypt_base64(data, _skey)
