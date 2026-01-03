"""
🔧 YTMA - Merkezi Logging Sistemi
Tüm modüller için standart logging altyapısı sağlar.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Log klasörü
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log dosya adı (günlük)
LOG_FILE = LOG_DIR / f"ytma_{datetime.now().strftime('%Y-%m-%d')}.log"

# Renkli konsol çıktısı için ANSI kodları
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Konsol için renkli log formatter"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BOLD + Colors.RED,
    }
    
    LEVEL_ICONS = {
        logging.DEBUG: "🔍",
        logging.INFO: "✅",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }
    
    def format(self, record):
        # Seviyeye göre renk ve ikon
        color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        icon = self.LEVEL_ICONS.get(record.levelno, "")
        
        # Orijinal mesajı formatla
        original_msg = record.msg
        record.msg = f"{icon} {color}{record.msg}{Colors.RESET}"
        
        result = super().format(record)
        record.msg = original_msg  # Orijinali geri yükle
        
        return result


class PlainFormatter(logging.Formatter):
    """Dosya için düz metin formatter"""
    
    LEVEL_ICONS = {
        logging.DEBUG: "[DEBUG]",
        logging.INFO: "[INFO]",
        logging.WARNING: "[WARN]",
        logging.ERROR: "[ERROR]",
        logging.CRITICAL: "[CRITICAL]",
    }
    
    def format(self, record):
        level_tag = self.LEVEL_ICONS.get(record.levelno, "[LOG]")
        record.levelname = level_tag
        return super().format(record)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Modül için logger oluşturur veya mevcut olanı döner.
    
    Args:
        name: Logger adı (genellikle modül adı, örn: "smart_bot")
        level: Log seviyesi (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Yapılandırılmış logger instance
    
    Kullanım:
        from logger import get_logger
        log = get_logger(__name__)
        log.info("Bu bir bilgi mesajı")
        log.warning("Bu bir uyarı")
        log.error("Bu bir hata")
    """
    logger = logging.getLogger(name)
    
    # Eğer zaten handler varsa, tekrar ekleme
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)  # En düşük seviye, handler'lar filtreler
    
    # --- KONSOL HANDLER (Renkli) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = ColoredFormatter(
        fmt="%(asctime)s │ %(name)-15s │ %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # --- DOSYA HANDLER (Rotating) ---
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Dosyaya her şeyi yaz
    file_format = PlainFormatter(
        fmt="%(asctime)s │ %(levelname)-10s │ %(name)-15s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Propagation'ı kapat (üst logger'lara iletme)
    logger.propagate = False
    
    return logger


# --- HAZIR LOGGER'LAR ---
# Ana modüller için önceden tanımlanmış logger'lar
def get_bot_logger():
    """SmartBot için logger"""
    return get_logger("smart_bot", logging.INFO)

def get_healer_logger():
    """Healer (Self-Healing) için logger"""
    return get_logger("healer", logging.INFO)

def get_recovery_logger():
    """Recovery Manager için logger"""
    return get_logger("recovery", logging.INFO)

def get_learning_logger():
    """Learning System için logger"""
    return get_logger("learning", logging.INFO)

def get_ai_logger():
    """AI Model için logger"""
    return get_logger("ai_model", logging.INFO)

def get_test_logger():
    """Test senaryoları için logger"""
    return get_logger("test", logging.INFO)


# --- PERFORMANS LOGGING ---
class PerformanceLogger:
    """İşlem sürelerini ölçmek için yardımcı sınıf"""
    
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"⏱️ Başladı: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(f"⏱️ Hata ile bitti: {self.operation_name} ({duration:.2f}s) - {exc_val}")
        else:
            self.logger.debug(f"⏱️ Tamamlandı: {self.operation_name} ({duration:.2f}s)")
        
        return False  # Exception'ı yutma


def timed(logger: logging.Logger):
    """
    Fonksiyon süresini ölçen decorator
    
    Kullanım:
        @timed(log)
        def my_function():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceLogger(logger, func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# --- TEST ---
if __name__ == "__main__":
    # Test logger'ları
    log = get_logger("test_module")
    
    log.debug("Bu bir debug mesajı - detaylı bilgi")
    log.info("Bu bir info mesajı - normal işlem")
    log.warning("Bu bir warning mesajı - dikkat edilmeli")
    log.error("Bu bir error mesajı - hata oluştu")
    log.critical("Bu bir critical mesajı - kritik hata!")
    
    # Performance logger testi
    import time
    with PerformanceLogger(log, "Test işlemi"):
        time.sleep(0.5)
    
    print(f"\n📁 Log dosyası: {LOG_FILE}")
