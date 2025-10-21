use base64::{engine::general_purpose::STANDARD, Engine};
use pyo3::exceptions::{PyValueError, PyException};
use pyo3::prelude::*;
use sha2::{Sha256, Digest};
use std::time::{SystemTime, UNIX_EPOCH};
use rand::{Rng, distributions::Alphanumeric};

#[pyclass]
pub struct ByfuidGenerator {
    encoding_chars: String,
}

#[pymethods]
impl ByfuidGenerator {
    #[new]
    pub fn new() -> Self {
        Self {
            encoding_chars: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".to_string(),
        }
    }

    pub fn generate_user_data(&self, length: usize) -> PyResult<String> {
        if length != 12 {
            return Err(PyValueError::new_err("用户自由数据必须为12字符"));
        }
        
        let mut rng = rand::thread_rng();
        let user_data: String = (0..length)
            .map(|_| rng.sample(Alphanumeric) as char)
            .collect();
        
        Ok(user_data)
    }

    pub fn generate_timestamp(&self) -> PyResult<String> {
        let start = SystemTime::now();
        let since_epoch = start.duration_since(UNIX_EPOCH)
            .map_err(|e| PyValueError::new_err(format!("时间获取失败: {}", e)))?;
        
        let timestamp_ms = since_epoch.as_millis();
        let timestamp_str = timestamp_ms.to_string();
        
        if timestamp_str.len() < 13 {
            Ok(format!("{:0>13}", timestamp_str))
        } else if timestamp_str.len() > 13 {
            Ok(timestamp_str[..13].to_string())
        } else {
            Ok(timestamp_str)
        }
    }

    pub fn generate_checksum(&self, data: &str, length: usize) -> PyResult<String> {
        if length != 24 {
            return Err(PyValueError::new_err("数据校验数据必须为24字符"));
        }

        let mut hasher = Sha256::new();
        hasher.update(data.as_bytes());
        let result = hasher.finalize();
        let checksum = format!("{:x}", result);
        
        Ok(checksum[..length].to_string())
    }

    //pub fn generate_custom_data(&self, custom_input: Option<String>, length: usize) -> PyResult<String>
    pub fn generate_custom_data(&self, length: usize, custom_input: Option<String>) -> PyResult<String> {
        if length != 201 {
            return Err(PyValueError::new_err("自定义数据必须为201字符"));
        }

        let custom_data = match custom_input {
            Some(input) => {
                let input_len = input.chars().count();
                if input_len > length {
                    input.chars().take(length).collect()
                } else if input_len < length {
                    let mut extended = input;
                    let mut rng = rand::thread_rng();
                    let chars: Vec<char> = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()你好世界欢迎编程开发技术数据验证安全加密".chars().collect();
                    
                    while extended.chars().count() < length {
                        let idx = rng.gen_range(0..chars.len());
                        extended.push(chars[idx]);
                    }
                    extended
                } else {
                    input
                }
            }
            None => {
                let mut rng = rand::thread_rng();
                let chars: Vec<char> = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()你好世界欢迎编程开发技术数据验证安全加密".chars().collect();
                let mut result = String::new();
                
                for _ in 0..length {
                    let idx = rng.gen_range(0..chars.len());
                    result.push(chars[idx]);
                }
                result
            }
        };

        Ok(custom_data)
    }

    fn custom_encode(&self, data: &str, password: &str) -> String {
        let password_bytes = password.as_bytes();
        let password_len = password_bytes.len();
        let mut encoded = Vec::with_capacity(data.len());
        
        for (i, byte) in data.bytes().enumerate() {
            let password_byte = password_bytes[i % password_len];
            encoded.push(byte ^ password_byte);
        }
        
        STANDARD.encode(&encoded)
    }

    pub fn generate_byfuid(&self, user_input: Option<String>, custom_input: Option<String>) -> PyResult<String> {
        // 验证用户输入数据
        let user_data = if let Some(input) = user_input {
            if input.chars().count() != 12 {
                return Err(PyValueError::new_err("用户自由数据必须为12字符"));
            }
            input
        } else {
            self.generate_user_data(12)?
        };

        // 生成自定义数据
        let custom_data = self.generate_custom_data(201, custom_input)?;

        // 生成时间戳
        let timestamp = self.generate_timestamp()?;

        // 生成校验和
        let partial_data = format!("{}{}{}", user_data, custom_data, timestamp);
        let checksum = self.generate_checksum(&partial_data, 24)?;

        // 组装数据
        let raw_data = format!("{}{}{}{}", user_data, custom_data, timestamp, checksum);
        let cleaned_data = raw_data.replace(' ', "+");

        // Base64编码
        let base64_encoded = STANDARD.encode(cleaned_data.as_bytes());

        // 自定义编码
        let custom_encoded = self.custom_encode(&base64_encoded, &timestamp);

        // 最终Base64编码并调整长度
        let final_base64 = STANDARD.encode(custom_encoded.as_bytes());
        
        let final_byfuid = if final_base64.len() > 512 {
            final_base64[..512].to_string()
        } else if final_base64.len() < 512 {
            let padding_needed = 512 - final_base64.len();
            format!("{}{}", final_base64, "+".repeat(padding_needed))
        } else {
            final_base64
        };

        Ok(final_byfuid)
    }

    pub fn validate_byfuid_length(&self, byfuid: &str) -> bool {
        byfuid.chars().count() == 512
    }
}

#[pymodule]
fn byfuid(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ByfuidGenerator>()?;
    Ok(())
}