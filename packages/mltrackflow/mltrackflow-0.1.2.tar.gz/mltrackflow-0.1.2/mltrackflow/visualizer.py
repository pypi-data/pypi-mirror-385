"""
Görselleştirme ve grafik oluşturma modülü.

Bu modül, eğitim sürecini ve model performansını görselleştirmek için
zengin araçlar sunar.
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Visualizer:
    """
    ML eğitim sürecini görselleştirmek için araç sınıfı.
    
    Attributes:
        tracker: ExperimentTracker instance (opsiyonel)
        style: Matplotlib stil
    
    Example:
        >>> viz = Visualizer(tracker=tracker)
        >>> viz.plot_metrics_comparison(["run_1", "run_2"])
    """
    
    def __init__(self, tracker: Optional[Any] = None, style: str = "seaborn-v0_8-darkgrid"):
        """
        Args:
            tracker: ExperimentTracker instance
            style: Matplotlib stil
        """
        self.tracker = tracker
        
        # Stil ayarla
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        
        # Renk paleti
        self.colors = sns.color_palette("husl", 10)
        
        # Türkçe karakter desteği
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    def plot_confusion_matrix(
        self,
        y_true,
        y_pred,
        labels: Optional[List[str]] = None,
        normalize: bool = False,
        title: str = "Karmaşıklık Matrisi",
        output_path: Optional[str] = None,
    ):
        """
        Karmaşıklık matrisi (confusion matrix) çiz.
        
        Args:
            y_true: Gerçek değerler
            y_pred: Tahmin değerleri
            labels: Sınıf etiketleri
            normalize: Normalize et mi?
            title: Grafik başlığı
            output_path: Kayıt yolu (opsiyonel)
        """
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(y_true, y_pred)
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='.2f' if normalize else 'd',
            cmap='Blues',
            xticklabels=labels,
            yticklabels=labels,
            cbar_kws={'label': 'Oran' if normalize else 'Sayı'}
        )
        
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.ylabel('Gerçek Değer', fontsize=12)
        plt.xlabel('Tahmin', fontsize=12)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_feature_importance(
        self,
        model,
        feature_names: Optional[List[str]] = None,
        top_n: int = 20,
        title: str = "Özellik Önem Dereceleri",
        output_path: Optional[str] = None,
    ):
        """
        Özellik önem derecelerini çiz.
        
        Args:
            model: Eğitilmiş model
            feature_names: Özellik isimleri
            top_n: En önemli N özellik
            title: Grafik başlığı
            output_path: Kayıt yolu
        """
        if not hasattr(model, 'feature_importances_'):
            warnings.warn("Model feature_importances_ özelliğine sahip değil")
            return
        
        importances = model.feature_importances_
        
        if feature_names is None:
            feature_names = [f"Feature {i}" for i in range(len(importances))]
        
        # DataFrame oluştur ve sırala
        df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False).head(top_n)
        
        # Grafik
        plt.figure(figsize=(10, max(6, top_n * 0.3)))
        bars = plt.barh(range(len(df)), df['importance'], color=self.colors[0])
        plt.yticks(range(len(df)), df['feature'])
        plt.xlabel('Önem Derecesi', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.gca().invert_yaxis()
        
        # Değerleri bar'ların üzerine yaz
        for i, (idx, row) in enumerate(df.iterrows()):
            plt.text(row['importance'], i, f" {row['importance']:.4f}",
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_learning_curve(
        self,
        train_scores: List[float],
        val_scores: List[float],
        metric_name: str = "Score",
        title: str = "Öğrenme Eğrisi",
        output_path: Optional[str] = None,
    ):
        """
        Öğrenme eğrisi çiz.
        
        Args:
            train_scores: Eğitim skorları
            val_scores: Validasyon skorları
            metric_name: Metrik adı
            title: Grafik başlığı
            output_path: Kayıt yolu
        """
        epochs = range(1, len(train_scores) + 1)
        
        plt.figure(figsize=(10, 6))
        plt.plot(epochs, train_scores, 'o-', label='Eğitim', 
                color=self.colors[0], linewidth=2, markersize=6)
        plt.plot(epochs, val_scores, 's-', label='Validasyon',
                color=self.colors[1], linewidth=2, markersize=6)
        
        plt.xlabel('Epoch', fontsize=12)
        plt.ylabel(metric_name, fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.legend(fontsize=11, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_metrics_comparison(
        self,
        run_names: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        title: str = "Model Karşılaştırması",
        output_path: Optional[str] = None,
    ):
        """
        Farklı run'ların metriklerini karşılaştır.
        
        Args:
            run_names: Karşılaştırılacak run adları
            metrics: Karşılaştırılacak metrikler
            title: Grafik başlığı
            output_path: Kayıt yolu
        """
        if self.tracker is None:
            raise ValueError("Bu fonksiyon için tracker gerekli")
        
        # Tüm run'ları al
        df = self.tracker.list_runs()
        
        if df.empty:
            print("Henüz run kaydı yok.")
            return
        
        # Belirli run'ları filtrele
        if run_names:
            df = df[df['run_name'].isin(run_names)]
        
        # Metrikleri belirle
        if metrics is None:
            # Numerik kolonları al
            metrics = df.select_dtypes(include=[np.number]).columns.tolist()
            metrics = [m for m in metrics if m not in ['duration_seconds']]
        
        if not metrics:
            print("Karşılaştırılacak metrik bulunamadı.")
            return
        
        # Grafik
        n_metrics = len(metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(6*n_metrics, 5))
        
        if n_metrics == 1:
            axes = [axes]
        
        for ax, metric in zip(axes, metrics):
            df_sorted = df.sort_values(metric, ascending=False)
            bars = ax.bar(range(len(df_sorted)), df_sorted[metric], 
                         color=self.colors[:len(df_sorted)])
            ax.set_xticks(range(len(df_sorted)))
            ax.set_xticklabels(df_sorted['run_name'], rotation=45, ha='right')
            ax.set_ylabel(metric, fontsize=11)
            ax.set_title(metric, fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Değerleri bar'ların üzerine yaz
            for i, (idx, row) in enumerate(df_sorted.iterrows()):
                value = row[metric]
                ax.text(i, value, f'{value:.3f}', 
                       ha='center', va='bottom', fontsize=9)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_residuals(
        self,
        y_true,
        y_pred,
        title: str = "Artık (Residual) Grafik",
        output_path: Optional[str] = None,
    ):
        """
        Regresyon için artık (residual) grafiği çiz.
        
        Args:
            y_true: Gerçek değerler
            y_pred: Tahmin değerleri
            title: Grafik başlığı
            output_path: Kayıt yolu
        """
        residuals = y_true - y_pred
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Residual scatter
        axes[0].scatter(y_pred, residuals, alpha=0.6, color=self.colors[0])
        axes[0].axhline(y=0, color='r', linestyle='--', linewidth=2)
        axes[0].set_xlabel('Tahmin Değerleri', fontsize=11)
        axes[0].set_ylabel('Artıklar (Residuals)', fontsize=11)
        axes[0].set_title('Artık Dağılımı', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Residual histogram
        axes[1].hist(residuals, bins=30, edgecolor='black', 
                    color=self.colors[1], alpha=0.7)
        axes[1].set_xlabel('Artıklar', fontsize=11)
        axes[1].set_ylabel('Frekans', fontsize=11)
        axes[1].set_title('Artık Histogramı', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='y')
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_roc_curve(
        self,
        y_true,
        y_proba,
        title: str = "ROC Eğrisi",
        output_path: Optional[str] = None,
    ):
        """
        ROC eğrisi çiz.
        
        Args:
            y_true: Gerçek değerler
            y_proba: Tahmin olasılıkları
            title: Grafik başlığı
            output_path: Kayıt yolu
        """
        from sklearn.metrics import roc_curve, auc
        
        # Binary classification için
        if len(y_proba.shape) > 1 and y_proba.shape[1] > 1:
            y_proba = y_proba[:, 1]
        
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 8))
        plt.plot(fpr, tpr, color=self.colors[0], linewidth=2,
                label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], 'r--', linewidth=2, label='Rastgele')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(title, fontsize=14, fontweight='bold', pad=20)
        plt.legend(loc='lower right', fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_data_distribution(
        self,
        data,
        columns: Optional[List[str]] = None,
        title: str = "Veri Dağılımı",
        output_path: Optional[str] = None,
    ):
        """
        Veri dağılımını görselleştir.
        
        Args:
            data: DataFrame veya array
            columns: Görselleştirilecek kolonlar
            title: Grafik başlığı
            output_path: Kayıt yolu
        """
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)
        
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        n_cols = min(len(columns), 4)
        n_rows = (len(columns) - 1) // n_cols + 1
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        axes = axes.flatten() if n_rows * n_cols > 1 else [axes]
        
        for i, col in enumerate(columns):
            if i >= len(axes):
                break
            
            axes[i].hist(data[col].dropna(), bins=30, edgecolor='black',
                        color=self.colors[i % len(self.colors)], alpha=0.7)
            axes[i].set_xlabel(col, fontsize=10)
            axes[i].set_ylabel('Frekans', fontsize=10)
            axes[i].set_title(f'{col} Dağılımı', fontsize=11, fontweight='bold')
            axes[i].grid(True, alpha=0.3, axis='y')
        
        # Boş subplot'ları gizle
        for i in range(len(columns), len(axes)):
            axes[i].set_visible(False)
        
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"[PLOT] Grafik kaydedildi: {output_path}")
        else:
            plt.show()
        
        plt.close()


