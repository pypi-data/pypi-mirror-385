"""
Deney takibi ve yönetimi için ana modül.

Bu modül, ML deneylerini kaydetme, izleme ve karşılaştırma işlevlerini sağlar.
"""

import os
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import warnings

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    classification_report,
)


class ExperimentTracker:
    """
    ML deneylerini takip etmek için ana sınıf.
    
    Bu sınıf, model eğitimi sırasında parametreleri, metrikleri ve modelleri
    otomatik olarak kaydeder ve organize eder.
    
    Attributes:
        experiment_name: Deney adı
        storage_path: Kayıt klasörü yolu
        auto_log: Otomatik loglama aktif mi?
    
    Example:
        >>> tracker = ExperimentTracker(experiment_name="my_experiment")
        >>> with tracker.start_run(run_name="test_1"):
        ...     tracker.log_params({"lr": 0.01})
        ...     tracker.log_metric("accuracy", 0.95)
    """
    
    def __init__(
        self,
        experiment_name: str = "default_experiment",
        storage_path: str = "./experiments",
        auto_log: bool = True,
        log_data_hash: bool = True,
        verbose: bool = True,
    ):
        """
        Args:
            experiment_name: Deney adı
            storage_path: Deneylerin kaydedileceği klasör
            auto_log: Otomatik loglama aktif mi?
            log_data_hash: Veri hash'ini kaydet mi?
            verbose: Detaylı çıktı göster mi?
        """
        self.experiment_name = experiment_name
        self.storage_path = Path(storage_path)
        self.auto_log = auto_log
        self.log_data_hash = log_data_hash
        self.verbose = verbose
        
        # Deney klasörünü oluştur
        self.experiment_path = self.storage_path / experiment_name
        self.experiment_path.mkdir(parents=True, exist_ok=True)
        
        # Metadata dosyası
        self.metadata_file = self.experiment_path / "experiment_metadata.json"
        self._load_or_create_metadata()
        
        # Aktif run bilgileri
        self.current_run = None
        self.current_run_data = None
        
        if self.verbose:
            print(f"✨ ExperimentTracker başlatıldı: {experiment_name}")
            print(f"📁 Kayıt yolu: {self.experiment_path}")
    
    def _load_or_create_metadata(self):
        """Deney metadata'sını yükle veya oluştur."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "experiment_name": self.experiment_name,
                "created_at": datetime.now().isoformat(),
                "runs": {},
                "total_runs": 0,
            }
            self._save_metadata()
    
    def _save_metadata(self):
        """Metadata'yı kaydet."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def start_run(self, run_name: Optional[str] = None) -> 'RunContext':
        """
        Yeni bir run başlat.
        
        Args:
            run_name: Run adı (opsiyonel, otomatik oluşturulur)
        
        Returns:
            RunContext: Context manager
        
        Example:
            >>> with tracker.start_run("test_run"):
            ...     # Eğitim kodu
            ...     pass
        """
        if run_name is None:
            run_name = f"run_{self.metadata['total_runs'] + 1}_{int(time.time())}"
        
        return RunContext(self, run_name)
    
    def _initialize_run(self, run_name: str):
        """Run'ı başlat (internal)."""
        self.current_run = run_name
        self.current_run_data = {
            "run_name": run_name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "params": {},
            "metrics": {},
            "tags": {},
            "artifacts": [],
            "status": "running",
        }
        
        # Run klasörünü oluştur
        run_path = self.experiment_path / run_name
        run_path.mkdir(exist_ok=True)
        
        if self.verbose:
            print(f"\n🚀 Run başlatıldı: {run_name}")
    
    def _finalize_run(self):
        """Run'ı sonlandır (internal)."""
        if self.current_run_data is None:
            return
        
        end_time = datetime.now()
        self.current_run_data["end_time"] = end_time.isoformat()
        
        # Süreyi hesapla
        start = datetime.fromisoformat(self.current_run_data["start_time"])
        duration = (end_time - start).total_seconds()
        self.current_run_data["duration_seconds"] = duration
        self.current_run_data["status"] = "completed"
        
        # Metadata'ya ekle
        self.metadata["runs"][self.current_run] = self.current_run_data
        self.metadata["total_runs"] += 1
        self._save_metadata()
        
        # Run verilerini kaydet
        run_file = self.experiment_path / self.current_run / "run_data.json"
        with open(run_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_run_data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"✅ Run tamamlandı: {self.current_run}")
            print(f"⏱️  Süre: {duration:.2f} saniye")
        
        self.current_run = None
        self.current_run_data = None
    
    def log_params(self, params: Dict[str, Any]):
        """
        Parametreleri kaydet.
        
        Args:
            params: Parametre sözlüğü
        
        Example:
            >>> tracker.log_params({"learning_rate": 0.01, "epochs": 100})
        """
        if self.current_run_data is None:
            warnings.warn("Aktif run yok. Önce start_run() çağırın.")
            return
        
        self.current_run_data["params"].update(params)
        
        if self.verbose:
            print(f"📝 Parametreler kaydedildi: {list(params.keys())}")
    
    def log_metric(self, key: str, value: Union[int, float]):
        """
        Tek bir metrik kaydet.
        
        Args:
            key: Metrik adı
            value: Metrik değeri
        
        Example:
            >>> tracker.log_metric("accuracy", 0.95)
        """
        if self.current_run_data is None:
            warnings.warn("Aktif run yok. Önce start_run() çağırın.")
            return
        
        self.current_run_data["metrics"][key] = value
        
        if self.verbose:
            print(f"📊 Metrik kaydedildi: {key} = {value:.4f}")
    
    def log_metrics(self, metrics: Dict[str, Union[int, float]]):
        """
        Birden fazla metrik kaydet.
        
        Args:
            metrics: Metrik sözlüğü
        
        Example:
            >>> tracker.log_metrics({"accuracy": 0.95, "f1_score": 0.93})
        """
        for key, value in metrics.items():
            self.log_metric(key, value)
    
    def log_model_metrics(
        self,
        model,
        X_test,
        y_test,
        task_type: str = "auto",
    ):
        """
        Model metriklerini otomatik hesapla ve kaydet.
        
        Args:
            model: Eğitilmiş model
            X_test: Test özellikleri
            y_test: Test hedef değerleri
            task_type: 'classification', 'regression' veya 'auto'
        
        Example:
            >>> tracker.log_model_metrics(model, X_test, y_test)
        """
        y_pred = model.predict(X_test)
        
        # Task tipini otomatik belirle
        if task_type == "auto":
            if hasattr(model, "predict_proba"):
                task_type = "classification"
            else:
                # Hedef değerlere bak
                if len(np.unique(y_test)) < 20:
                    task_type = "classification"
                else:
                    task_type = "regression"
        
        metrics = {}
        
        if task_type == "classification":
            metrics["accuracy"] = accuracy_score(y_test, y_pred)
            metrics["precision"] = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            metrics["recall"] = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            metrics["f1_score"] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Classification report'u kaydet
            report = classification_report(y_test, y_pred)
            report_file = self.experiment_path / self.current_run / "classification_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            
        elif task_type == "regression":
            metrics["mse"] = mean_squared_error(y_test, y_pred)
            metrics["rmse"] = np.sqrt(metrics["mse"])
            metrics["mae"] = mean_absolute_error(y_test, y_pred)
            metrics["r2_score"] = r2_score(y_test, y_pred)
        
        self.log_metrics(metrics)
        
        if self.verbose:
            print(f"📈 {task_type.capitalize()} metrikleri otomatik kaydedildi")
    
    def save_model(self, model, model_name: str):
        """
        Modeli kaydet.
        
        Args:
            model: Kaydedilecek model
            model_name: Model dosya adı
        
        Example:
            >>> tracker.save_model(model, "my_model")
        """
        if self.current_run_data is None:
            warnings.warn("Aktif run yok. Önce start_run() çağırın.")
            return
        
        model_path = self.experiment_path / self.current_run / f"{model_name}.joblib"
        joblib.dump(model, model_path)
        
        self.current_run_data["artifacts"].append({
            "type": "model",
            "name": model_name,
            "path": str(model_path),
        })
        
        if self.verbose:
            print(f"💾 Model kaydedildi: {model_path}")
    
    def log_dataset_hash(self, X, y=None):
        """
        Veri setinin hash'ini hesapla ve kaydet.
        
        Args:
            X: Özellikler
            y: Hedef değerler (opsiyonel)
        """
        if not self.log_data_hash:
            return
        
        # Hash hesapla
        X_bytes = pd.DataFrame(X).to_json().encode()
        data_hash = hashlib.md5(X_bytes).hexdigest()
        
        self.log_params({"data_hash_X": data_hash})
        
        if y is not None:
            y_bytes = pd.Series(y).to_json().encode()
            y_hash = hashlib.md5(y_bytes).hexdigest()
            self.log_params({"data_hash_y": y_hash})
        
        if self.verbose:
            print(f"🔒 Veri hash'i kaydedildi: {data_hash[:8]}...")
    
    def list_runs(self) -> pd.DataFrame:
        """
        Tüm run'ları listele.
        
        Returns:
            DataFrame: Run bilgileri
        
        Example:
            >>> df = tracker.list_runs()
            >>> print(df)
        """
        if not self.metadata["runs"]:
            print("Henüz run kaydı yok.")
            return pd.DataFrame()
        
        runs_data = []
        for run_name, run_info in self.metadata["runs"].items():
            row = {
                "run_name": run_name,
                "start_time": run_info["start_time"],
                "duration_seconds": run_info.get("duration_seconds", None),
                "status": run_info["status"],
            }
            row.update(run_info["metrics"])
            runs_data.append(row)
        
        return pd.DataFrame(runs_data)
    
    def get_best_run(self, metric: str, maximize: bool = True) -> Optional[str]:
        """
        En iyi run'ı bul.
        
        Args:
            metric: Karşılaştırma metriği
            maximize: True ise maksimize, False ise minimize et
        
        Returns:
            str: En iyi run adı
        
        Example:
            >>> best = tracker.get_best_run("accuracy", maximize=True)
        """
        df = self.list_runs()
        if df.empty or metric not in df.columns:
            return None
        
        if maximize:
            best_idx = df[metric].idxmax()
        else:
            best_idx = df[metric].idxmin()
        
        return df.loc[best_idx, "run_name"]
    
    def load_model(self, run_name: str, model_name: str):
        """
        Kaydedilmiş modeli yükle.
        
        Args:
            run_name: Run adı
            model_name: Model adı
        
        Returns:
            Model nesnesi
        
        Example:
            >>> model = tracker.load_model("run_1", "my_model")
        """
        model_path = self.experiment_path / run_name / f"{model_name}.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model bulunamadı: {model_path}")
        
        return joblib.load(model_path)
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        HTML rapor oluştur.
        
        Args:
            output_path: Çıktı dosya yolu (opsiyonel)
        
        Returns:
            str: Rapor dosya yolu
        """
        from .report_generator import ReportGenerator
        
        generator = ReportGenerator(self)
        report_path = generator.generate(output_path)
        
        if self.verbose:
            print(f"📄 Rapor oluşturuldu: {report_path}")
        
        return report_path
    
    @classmethod
    def from_config(cls, config_path: str) -> 'ExperimentTracker':
        """
        YAML config dosyasından tracker oluştur.
        
        Args:
            config_path: Config dosya yolu
        
        Returns:
            ExperimentTracker: Yeni tracker instance
        """
        from .utils import load_config
        
        config = load_config(config_path)
        exp_config = config.get("experiment", {})
        tracking_config = config.get("tracking", {})
        
        return cls(
            experiment_name=exp_config.get("name", "default_experiment"),
            storage_path=exp_config.get("storage_path", "./experiments"),
            auto_log=tracking_config.get("auto_log", True),
            log_data_hash=tracking_config.get("log_data_hash", True),
        )


class RunContext:
    """Context manager for experiment runs."""
    
    def __init__(self, tracker: ExperimentTracker, run_name: str):
        self.tracker = tracker
        self.run_name = run_name
    
    def __enter__(self):
        self.tracker._initialize_run(self.run_name)
        return self.tracker
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.tracker.current_run_data["status"] = "failed"
            self.tracker.current_run_data["error"] = str(exc_val)
        self.tracker._finalize_run()
        return False


