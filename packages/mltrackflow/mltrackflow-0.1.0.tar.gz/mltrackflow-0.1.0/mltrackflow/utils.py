"""
Yardımcı fonksiyonlar ve araçlar.
"""

import logging
import yaml
from pathlib import Path
from typing import Any, Dict


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
):
    """
    Loglama sistemini yapılandır.
    
    Args:
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log dosya yolu (opsiyonel)
        format: Log mesaj formatı
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format,
        handlers=handlers,
    )
    
    logger = logging.getLogger("mltrackflow")
    logger.info(f"Loglama sistemi başlatıldı: {level}")
    
    return logger


def load_config(config_path: str) -> Dict[str, Any]:
    """
    YAML config dosyasını yükle.
    
    Args:
        config_path: Config dosya yolu
    
    Returns:
        Dict: Config verisi
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config dosyası bulunamadı: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def save_config(config: Dict[str, Any], output_path: str):
    """
    Config'i YAML olarak kaydet.
    
    Args:
        config: Config verisi
        output_path: Çıktı dosya yolu
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Config kaydedildi: {output_path}")


def format_duration(seconds: float) -> str:
    """
    Süreyi okunabilir formatta göster.
    
    Args:
        seconds: Saniye cinsinden süre
    
    Returns:
        str: Formatlanmış süre
    """
    if seconds < 60:
        return f"{seconds:.2f} saniye"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} dakika"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} saat"


def get_sklearn_model_type(model) -> str:
    """
    Sklearn modelinin tipini belirle.
    
    Args:
        model: Sklearn model
    
    Returns:
        str: 'classifier', 'regressor' veya 'unknown'
    """
    from sklearn.base import is_classifier, is_regressor
    
    if is_classifier(model):
        return 'classifier'
    elif is_regressor(model):
        return 'regressor'
    else:
        return 'unknown'


def print_welcome_message():
    """Hoş geldin mesajı yazdır."""
    message = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              🚀 MLTrackFlow v0.1.0 🚀                    ║
    ║                                                          ║
    ║   Makine Öğrenimi Eğitim Süreçlerini Şeffaf ve          ║
    ║          İzlenebilir Hale Getiren Kütüphane             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    📚 Dokümantasyon: https://mltrackflow.readthedocs.io
    💬 Destek: https://github.com/yourusername/mltrackflow/issues
    """
    print(message)


