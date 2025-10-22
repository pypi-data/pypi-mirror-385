"""
Model karşılaştırma modülü.

Bu modül, farklı model denemelerini karşılaştırmak için araçlar sunar.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from tabulate import tabulate


class ModelComparator:
    """
    Farklı model denemelerini karşılaştırmak için sınıf.
    
    Attributes:
        tracker: ExperimentTracker instance
    
    Example:
        >>> comparator = ModelComparator(tracker=tracker)
        >>> comparator.compare_runs(["run_1", "run_2", "run_3"])
        >>> comparator.print_comparison_table()
    """
    
    def __init__(self, tracker: Any):
        """
        Args:
            tracker: ExperimentTracker instance
        """
        self.tracker = tracker
        self.comparison_df = None
    
    def compare_runs(
        self,
        run_names: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Run'ları karşılaştır.
        
        Args:
            run_names: Karşılaştırılacak run'lar (None ise hepsi)
            metrics: Karşılaştırılacak metrikler (None ise hepsi)
        
        Returns:
            DataFrame: Karşılaştırma tablosu
        """
        # Tüm run'ları al
        df = self.tracker.list_runs()
        
        if df.empty:
            print("Henüz run kaydı yok.")
            return pd.DataFrame()
        
        # Belirli run'ları filtrele
        if run_names:
            df = df[df['run_name'].isin(run_names)]
        
        # Belirli metrikleri filtrele
        if metrics:
            cols = ['run_name', 'start_time', 'duration_seconds', 'status'] + \
                   [m for m in metrics if m in df.columns]
            df = df[cols]
        
        self.comparison_df = df
        return df
    
    def print_comparison_table(self, tablefmt: str = "fancy_grid"):
        """
        Karşılaştırma tablosunu yazdır.
        
        Args:
            tablefmt: Tablo formatı (tabulate formatı)
        """
        if self.comparison_df is None or self.comparison_df.empty:
            print("Karşılaştırma verisi yok. Önce compare_runs() çağırın.")
            return
        
        print("\n" + "="*80)
        print("[COMPARE] MODEL KARŞILAŞTIRMA TABLOSU")
        print("="*80 + "\n")
        
        print(tabulate(
            self.comparison_df,
            headers='keys',
            tablefmt=tablefmt,
            showindex=False,
            floatfmt=".4f"
        ))
        
        print("\n" + "="*80 + "\n")
    
    def get_best_model(
        self,
        metric: str,
        maximize: bool = True,
    ) -> Optional[str]:
        """
        En iyi modeli bul.
        
        Args:
            metric: Karşılaştırma metriği
            maximize: True ise maksimize, False ise minimize
        
        Returns:
            str: En iyi run adı
        """
        if self.comparison_df is None or self.comparison_df.empty:
            print("Karşılaştırma verisi yok. Önce compare_runs() çağırın.")
            return None
        
        if metric not in self.comparison_df.columns:
            print(f"Metrik bulunamadı: {metric}")
            return None
        
        if maximize:
            best_idx = self.comparison_df[metric].idxmax()
        else:
            best_idx = self.comparison_df[metric].idxmin()
        
        best_run = self.comparison_df.loc[best_idx, 'run_name']
        best_value = self.comparison_df.loc[best_idx, metric]
        
        print(f"\n[BEST] En iyi model: {best_run}")
        print(f"[SCORE] {metric}: {best_value:.4f}\n")
        
        return best_run
    
    def plot_comparison(self, metrics: Optional[List[str]] = None):
        """
        Karşılaştırma grafiğini çiz.
        
        Args:
            metrics: Görselleştirilecek metrikler
        """
        from .visualizer import Visualizer
        
        if self.comparison_df is None or self.comparison_df.empty:
            print("Karşılaştırma verisi yok. Önce compare_runs() çağırın.")
            return
        
        viz = Visualizer(tracker=self.tracker)
        run_names = self.comparison_df['run_name'].tolist()
        viz.plot_metrics_comparison(run_names=run_names, metrics=metrics)
    
    def generate_comparison_report(self, output_path: str):
        """
        Karşılaştırma raporu oluştur.
        
        Args:
            output_path: Çıktı dosya yolu
        """
        if self.comparison_df is None or self.comparison_df.empty:
            print("Karşılaştırma verisi yok. Önce compare_runs() çağırın.")
            return
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# MODEL KARŞILAŞTIRMA RAPORU\n\n")
            f.write(f"Toplam Model Sayısı: {len(self.comparison_df)}\n\n")
            
            f.write("## Karşılaştırma Tablosu\n\n")
            f.write("```\n")
            f.write(tabulate(
                self.comparison_df,
                headers='keys',
                tablefmt="grid",
                showindex=False,
                floatfmt=".4f"
            ))
            f.write("\n```\n\n")
            
            # İstatistikler
            numeric_cols = self.comparison_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                f.write("## Metrik İstatistikleri\n\n")
                for col in numeric_cols:
                    if col != 'duration_seconds':
                        mean_val = self.comparison_df[col].mean()
                        std_val = self.comparison_df[col].std()
                        min_val = self.comparison_df[col].min()
                        max_val = self.comparison_df[col].max()
                        
                        f.write(f"### {col}\n")
                        f.write(f"- Ortalama: {mean_val:.4f}\n")
                        f.write(f"- Standart Sapma: {std_val:.4f}\n")
                        f.write(f"- Min: {min_val:.4f}\n")
                        f.write(f"- Max: {max_val:.4f}\n\n")
        
        print(f"[REPORT] Karşılaştırma raporu oluşturuldu: {output_path}")


