"""
ML Pipeline yönetimi için modül.

Bu modül, veri hazırlamadan model eğitimine kadar tüm adımları
modüler ve izlenebilir şekilde yönetmenizi sağlar.
"""

from typing import Any, Dict, List, Optional, Union
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline as SKPipeline


class PipelineStep:
    """
    Pipeline'da bir adımı temsil eden sınıf.
    
    Attributes:
        name: Adım adı
        transformer: Sklearn transformer veya model
        description: Adım açıklaması
    
    Example:
        >>> from sklearn.preprocessing import StandardScaler
        >>> step = PipelineStep(name="scaling", transformer=StandardScaler())
    """
    
    def __init__(
        self,
        name: str,
        transformer: Optional[Any] = None,
        model: Optional[Any] = None,
        description: str = "",
    ):
        """
        Args:
            name: Adım adı
            transformer: Sklearn transformer (opsiyonel)
            model: Sklearn model (opsiyonel)
            description: Adım açıklaması
        """
        self.name = name
        self.transformer = transformer
        self.model = model
        self.description = description
        self.is_fitted = False
        self.input_shape = None
        self.output_shape = None
        
        if transformer is None and model is None:
            raise ValueError("transformer veya model belirtilmeli")
        
        # Model varsa onu transformer olarak kullan
        if model is not None:
            self.transformer = model
            self.is_model = True
        else:
            self.is_model = False
    
    def fit(self, X, y=None):
        """Adımı eğit."""
        self.input_shape = X.shape if hasattr(X, 'shape') else None
        self.transformer.fit(X, y)
        self.is_fitted = True
        return self
    
    def transform(self, X):
        """Adımı uygula."""
        if not self.is_fitted:
            raise RuntimeError(f"Adım henüz eğitilmedi: {self.name}")
        
        if self.is_model:
            # Model ise predict kullan
            return self.transformer.predict(X)
        else:
            # Transformer ise transform kullan
            result = self.transformer.transform(X)
            self.output_shape = result.shape if hasattr(result, 'shape') else None
            return result
    
    def fit_transform(self, X, y=None):
        """Eğit ve uygula."""
        self.fit(X, y)
        return self.transform(X)
    
    def get_info(self) -> Dict[str, Any]:
        """Adım bilgilerini döndür."""
        return {
            "name": self.name,
            "type": type(self.transformer).__name__,
            "description": self.description,
            "is_fitted": self.is_fitted,
            "is_model": self.is_model,
            "input_shape": self.input_shape,
            "output_shape": self.output_shape,
            "params": self.transformer.get_params() if hasattr(self.transformer, 'get_params') else {},
        }


class MLPipeline:
    """
    ML Pipeline yönetimi için ana sınıf.
    
    Bu sınıf, veri hazırlama, özellik mühendisliği ve model eğitimi gibi
    adımları zincirleme olarak yönetir ve her adımı izlenebilir kılar.
    
    Attributes:
        name: Pipeline adı
        steps: Pipeline adımları listesi
        tracker: ExperimentTracker instance (opsiyonel)
    
    Example:
        >>> pipeline = MLPipeline(name="iris_pipeline")
        >>> pipeline.add_step(PipelineStep(name="scaling", transformer=StandardScaler()))
        >>> pipeline.add_step(PipelineStep(name="model", model=RandomForestClassifier()))
        >>> pipeline.fit(X_train, y_train)
        >>> predictions = pipeline.predict(X_test)
    """
    
    def __init__(
        self,
        name: str = "ml_pipeline",
        tracker: Optional[Any] = None,
        verbose: bool = True,
    ):
        """
        Args:
            name: Pipeline adı
            tracker: ExperimentTracker instance (opsiyonel)
            verbose: Detaylı çıktı göster mi?
        """
        self.name = name
        self.tracker = tracker
        self.verbose = verbose
        self.steps: List[PipelineStep] = []
        self.is_fitted = False
        self.fit_time = None
        
        if self.verbose:
            print(f"[PIPELINE] Oluşturuldu: {name}")
    
    def add_step(self, step: PipelineStep):
        """
        Pipeline'a yeni adım ekle.
        
        Args:
            step: PipelineStep instance
        
        Example:
            >>> pipeline.add_step(PipelineStep(name="pca", transformer=PCA(n_components=2)))
        """
        self.steps.append(step)
        
        if self.verbose:
            print(f"[STEP] Eklendi: {step.name} ({type(step.transformer).__name__})")
    
    def fit(self, X, y=None):
        """
        Pipeline'ı eğit.
        
        Args:
            X: Eğitim özellikleri
            y: Eğitim hedef değerleri
        
        Returns:
            self
        """
        import time
        
        if not self.steps:
            raise ValueError("Pipeline'da adım yok. add_step() ile adım ekleyin.")
        
        if self.verbose:
            print(f"\n[TRAIN] Pipeline eğitimi başladı: {self.name}")
            print(f"[INFO] Toplam {len(self.steps)} adım")
        
        start_time = time.time()
        X_current = X
        
        # Her adımı sırayla eğit
        for i, step in enumerate(self.steps[:-1], 1):  # Son adım hariç
            if self.verbose:
                print(f"\n[{i}/{len(self.steps)}] {step.name} eğitiliyor...")
            
            step.fit(X_current, y)
            X_current = step.transform(X_current)
            
            if self.verbose:
                if hasattr(X_current, 'shape'):
                    print(f"    [OK] Çıktı boyutu: {X_current.shape}")
        
        # Son adım (genelde model)
        final_step = self.steps[-1]
        if self.verbose:
            print(f"\n[{len(self.steps)}/{len(self.steps)}] {final_step.name} eğitiliyor...")
        
        final_step.fit(X_current, y)
        
        self.fit_time = time.time() - start_time
        self.is_fitted = True
        
        if self.verbose:
            print(f"\n[DONE] Pipeline eğitimi tamamlandı!")
            print(f"[TIME] Süre: {self.fit_time:.2f} saniye")
        
        # Tracker'a kaydet
        if self.tracker is not None:
            self._log_to_tracker()
        
        return self
    
    def predict(self, X):
        """
        Pipeline ile tahmin yap.
        
        Args:
            X: Test özellikleri
        
        Returns:
            Tahminler
        """
        if not self.is_fitted:
            raise RuntimeError("Pipeline henüz eğitilmedi. Önce fit() çağırın.")
        
        X_current = X
        
        # Tüm adımları uygula
        for step in self.steps[:-1]:  # Son adım hariç
            X_current = step.transform(X_current)
        
        # Son adım (model) ile tahmin
        final_step = self.steps[-1]
        return final_step.transform(X_current)
    
    def fit_predict(self, X, y=None):
        """Eğit ve tahmin yap."""
        self.fit(X, y)
        return self.predict(X)
    
    def transform(self, X):
        """
        Pipeline'ı uygula (model adımı hariç).
        
        Args:
            X: Özellikler
        
        Returns:
            Dönüştürülmüş özellikler
        """
        if not self.is_fitted:
            raise RuntimeError("Pipeline henüz eğitilmedi. Önce fit() çağırın.")
        
        X_current = X
        
        # Model adımı dışındaki adımları uygula
        for step in self.steps[:-1]:
            X_current = step.transform(X_current)
        
        return X_current
    
    def get_step(self, name: str) -> Optional[PipelineStep]:
        """
        İsme göre adım getir.
        
        Args:
            name: Adım adı
        
        Returns:
            PipelineStep veya None
        """
        for step in self.steps:
            if step.name == name:
                return step
        return None
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Pipeline bilgilerini döndür.
        
        Returns:
            Dict: Pipeline bilgileri
        """
        return {
            "name": self.name,
            "is_fitted": self.is_fitted,
            "fit_time": self.fit_time,
            "total_steps": len(self.steps),
            "steps": [step.get_info() for step in self.steps],
        }
    
    def visualize_steps(self, output_path: Optional[str] = None):
        """
        Pipeline adımlarını görselleştir.
        
        Args:
            output_path: Çıktı dosya yolu (opsiyonel)
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.patches import FancyBboxPatch
        except ImportError:
            warnings.warn("Görselleştirme için matplotlib gerekli")
            return
        
        fig, ax = plt.subplots(figsize=(12, max(6, len(self.steps) * 1.5)))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, len(self.steps) + 1)
        ax.axis('off')
        
        # Başlık
        ax.text(5, len(self.steps) + 0.5, f"Pipeline: {self.name}",
                ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Her adımı çiz
        for i, step in enumerate(self.steps):
            y_pos = len(self.steps) - i - 0.5
            
            # Kutu
            color = '#4CAF50' if step.is_fitted else '#FFC107'
            box = FancyBboxPatch(
                (1, y_pos - 0.3), 8, 0.6,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='black', linewidth=2, alpha=0.7
            )
            ax.add_patch(box)
            
            # Adım bilgisi
            step_text = f"{i+1}. {step.name}\n{type(step.transformer).__name__}"
            ax.text(5, y_pos, step_text, ha='center', va='center',
                    fontsize=11, fontweight='bold')
            
            # Shape bilgisi
            if step.input_shape and step.output_shape:
                shape_text = f"{step.input_shape} → {step.output_shape}"
                ax.text(9.5, y_pos, shape_text, ha='left', va='center',
                        fontsize=9, style='italic')
            
            # Ok çiz (son adım hariç)
            if i < len(self.steps) - 1:
                ax.arrow(5, y_pos - 0.3, 0, -0.35, head_width=0.3,
                        head_length=0.1, fc='black', ec='black')
        
        # Legend
        fitted_patch = mpatches.Patch(color='#4CAF50', label='Eğitilmiş')
        unfitted_patch = mpatches.Patch(color='#FFC107', label='Eğitilmemiş')
        ax.legend(handles=[fitted_patch, unfitted_patch], loc='lower right')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            if self.verbose:
                print(f"[PLOT] Pipeline görselleştirildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def _log_to_tracker(self):
        """Pipeline bilgilerini tracker'a kaydet."""
        if self.tracker is None or self.tracker.current_run_data is None:
            return
        
        # Pipeline bilgilerini params olarak kaydet
        self.tracker.log_params({
            "pipeline_name": self.name,
            "pipeline_steps": len(self.steps),
            "pipeline_fit_time": self.fit_time,
        })
        
        # Her adımın parametrelerini kaydet
        for step in self.steps:
            step_info = step.get_info()
            prefix = f"step_{step.name}_"
            
            self.tracker.log_params({
                f"{prefix}type": step_info["type"],
            })
            
            # Adım parametrelerini kaydet
            for param_name, param_value in step_info["params"].items():
                try:
                    # JSON serialize edilebilir mi kontrol et
                    import json
                    json.dumps(param_value)
                    self.tracker.log_params({f"{prefix}{param_name}": param_value})
                except (TypeError, ValueError):
                    # Serialize edilemezse string'e çevir
                    self.tracker.log_params({f"{prefix}{param_name}": str(param_value)})
    
    def to_sklearn_pipeline(self) -> SKPipeline:
        """
        Sklearn Pipeline'a dönüştür.
        
        Returns:
            sklearn.pipeline.Pipeline
        """
        steps = [(step.name, step.transformer) for step in self.steps]
        return SKPipeline(steps)
    
    def save(self, path: str):
        """
        Pipeline'ı kaydet.
        
        Args:
            path: Kayıt yolu
        """
        import joblib
        
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self, save_path)
        
        if self.verbose:
            print(f"[SAVE] Pipeline kaydedildi: {save_path}")
    
    @staticmethod
    def load(path: str) -> 'MLPipeline':
        """
        Pipeline'ı yükle.
        
        Args:
            path: Dosya yolu
        
        Returns:
            MLPipeline instance
        """
        import joblib
        
        return joblib.load(path)


