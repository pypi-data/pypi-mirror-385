"""
BYFUID Generator - 高性能 BYFUID 生成库
结合 Rust 后端实现，提供快速安全的 BYFUID 生成功能。
"""

import sys
from typing import Optional

# Rust 扩展可用性检测
try:
    from .byfuid import ByfuidGenerator
    RUST_AVAILABLE = True
except ImportError as e:
    RUST_AVAILABLE = False
    print(f"警告: Rust 扩展加载失败，使用纯 Python 实现: {e}", file=sys.stderr)

# 纯 Python 回退实现
if not RUST_AVAILABLE:
    import base64
    import hashlib
    import random
    import time
    
    class ByfuidGenerator:
        """纯 Python 回退实现"""
        
        def __init__(self):
            self.encoding_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        
        def generate_user_data(self, length: int = 12) -> str:
            if length != 12:
                raise ValueError("用户自由数据必须为12字符")
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            return ''.join(random.choice(chars) for _ in range(length))
        
        def generate_timestamp(self) -> str:
            timestamp = str(int(time.time() * 1000))
            if len(timestamp) < 13:
                return timestamp.zfill(13)
            elif len(timestamp) > 13:
                return timestamp[:13]
            return timestamp
        
        def generate_checksum(self, data: str, length: int = 24) -> str:
            if length != 24:
                raise ValueError("数据校验数据必须为24字符")
            return hashlib.sha256(data.encode()).hexdigest()[:length]
        
        def generate_custom_data(self, length: int = 201, custom_input: Optional[str] = None) -> str:
            if length != 201:
                raise ValueError("自定义数据必须为201字符")
            
            if custom_input:
                # 去除输入中的换行符
                cleaned_input = custom_input.replace('\n', '').replace('\r', '')
                if len(cleaned_input) > length:
                    return cleaned_input[:length]
                elif len(cleaned_input) < length:
                    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()你好世界欢迎编程开发技术数据验证安全加密"
                    result = cleaned_input
                    while len(result) < length:
                        result += random.choice(chars)
                    return result
                return cleaned_input
            else:
                chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()你好世界欢迎编程开发技术数据验证安全加密"
                return ''.join(random.choice(chars) for _ in range(length))
        
        def custom_encode(self, data: str, password: str) -> str:
            encoded = []
            password_len = len(password)
            for i, char in enumerate(data):
                password_char = password[i % password_len]
                encoded_char = chr(ord(char) ^ ord(password_char))
                encoded.append(encoded_char)
            return ''.join(encoded)
        
        def remove_newlines(self, text: str) -> str:
            """去除字符串中的所有换行符"""
            return text.replace('\n', '').replace('\r', '')
        
        def generate_byfuid(self, user_input: Optional[str] = None, custom_input: Optional[str] = None) -> str:
            # 用户数据
            if user_input:
                # 去除用户输入中的换行符
                user_input = self.remove_newlines(user_input)
                if len(user_input) != 12:
                    raise ValueError("用户自由数据必须为12字符")
            user_data = user_input or self.generate_user_data()
            
            # 自定义数据
            custom_data = self.generate_custom_data(201, custom_input)
            
            # 时间戳
            timestamp = self.generate_timestamp()
            
            # 校验和
            partial_data = user_data + custom_data + timestamp
            checksum = self.generate_checksum(partial_data)
            
            # 组装
            raw_data = user_data + custom_data + timestamp + checksum
            cleaned_data = raw_data.replace(' ', '+')
            
            # 编码
            base64_encoded = base64.b64encode(cleaned_data.encode()).decode()
            custom_encoded = self.custom_encode(base64_encoded, timestamp)
            final_base64 = base64.b64encode(custom_encoded.encode()).decode()
            
            # 去除所有换行符并调整长度
            final_byfuid = self.remove_newlines(final_base64)
            
            if len(final_byfuid) > 512:
                return final_byfuid[:512]
            elif len(final_byfuid) < 512:
                return final_byfuid + '+' * (512 - len(final_byfuid))
            return final_byfuid
        
        def validate_byfuid_length(self, byfuid: str) -> bool:
            return len(byfuid) == 512

# 创建全局实例
_generator = ByfuidGenerator()

# 公共API函数
def generate_byfuid(user_data: Optional[str] = None, custom_data: Optional[str] = None) -> str:
    """
    生成 BYFUID
    
    Args:
        user_data: 12字符用户数据（可选）
        custom_data: 自定义数据（可选）
        
    Returns:
        str: 512字符的BYFUID（已去除换行符）
    """
    return _generator.generate_byfuid(user_data, custom_data)

def validate_byfuid_length(byfuid: str) -> bool:
    """
    验证 BYFUID 长度
    
    Args:
        byfuid: 要验证的BYFUID
        
    Returns:
        bool: 长度是否有效
    """
    return _generator.validate_byfuid_length(byfuid)

# 导出公共API
__all__ = ['generate_byfuid', 'validate_byfuid_length', 'RUST_AVAILABLE']
__version__ = '0.1.1'