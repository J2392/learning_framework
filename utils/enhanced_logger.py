import logging
import os
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import datetime

class CustomJsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def format(self, record):
        logobj = {
            'timestamp': datetime.datetime.now().isoformat(),
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName
        }
        
        # Thêm exception info nếu có
        if record.exc_info:
            logobj['exception'] = self.formatException(record.exc_info)
        
        # Thêm custom fields nếu có
        if hasattr(record, 'data'):
            logobj['data'] = record.data
            
        return json.dumps(logobj)

def setup_enhanced_logger(name, log_dir='logs', 
                         json_format=True, max_bytes=10485760, 
                         backup_count=5, log_level=logging.INFO):
    """
    Thiết lập logger với nhiều tùy chọn nâng cao
    
    :param name: Tên của logger
    :param log_dir: Thư mục chứa file log
    :param json_format: Sử dụng JSON format hay không
    :param max_bytes: Kích thước tối đa của file log trước khi rotate
    :param backup_count: Số lượng file backup tối đa
    :param log_level: Mức độ logging (DEBUG, INFO, etc.)
    :return: Logger object
    """
    # Tạo thư mục log nếu chưa tồn tại
    os.makedirs(log_dir, exist_ok=True)
    
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Xóa handlers cũ nếu có
    if logger.handlers:
        logger.handlers.clear()
    
    # Tạo formatter
    if json_format:
        formatter = CustomJsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler - luôn hiển thị log ra console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler với rotation theo kích thước
    size_handler = RotatingFileHandler(
        os.path.join(log_dir, f"{name}.log"),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    size_handler.setFormatter(formatter)
    logger.addHandler(size_handler)
    
    # File handler với rotation theo thời gian (hàng ngày)
    time_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, f"{name}_daily.log"),
        when='midnight',
        interval=1,
        backupCount=30,  # Giữ log 30 ngày
        encoding='utf-8'
    )
    time_handler.setFormatter(formatter)
    logger.addHandler(time_handler)
    
    return logger

# Các helper functions để ghi log nâng cao
def log_api_call(logger, endpoint, payload=None, response=None, status_code=None, duration=None):
    """Log thông tin API call với data cấu trúc"""
    logger.info(
        f"API Call: {endpoint}", 
        extra={
            'data': {
                'endpoint': endpoint,
                'payload': payload,
                'response_snippet': str(response)[:200] if response else None,
                'status_code': status_code,
                'duration_ms': duration
            }
        }
    )

def log_error(logger, message, error=None, context=None):
    """Log lỗi với context đầy đủ"""
    logger.error(
        message,
        exc_info=error,
        extra={'data': context} if context else {}
    )

def log_user_activity(logger, user_id, action, details=None):
    """Log hoạt động người dùng"""
    logger.info(
        f"User {user_id}: {action}",
        extra={'data': {'user_id': user_id, 'action': action, 'details': details}}
    )
