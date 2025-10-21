"""
HTML rapor oluşturucu modül.
"""

from pathlib import Path
from datetime import datetime
from typing import Any, Optional
import base64
from io import BytesIO


class ReportGenerator:
    """
    HTML rapor oluşturucu.
    
    Attributes:
        tracker: ExperimentTracker instance
    """
    
    def __init__(self, tracker: Any):
        """
        Args:
            tracker: ExperimentTracker instance
        """
        self.tracker = tracker
    
    def generate(self, output_path: Optional[str] = None) -> str:
        """
        HTML rapor oluştur.
        
        Args:
            output_path: Çıktı dosya yolu
        
        Returns:
            str: Rapor dosya yolu
        """
        if output_path is None:
            output_path = self.tracker.experiment_path / "experiment_report.html"
        else:
            output_path = Path(output_path)
        
        # Rapor içeriğini oluştur
        html_content = self._generate_html()
        
        # Dosyaya yaz
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_html(self) -> str:
        """HTML içeriği oluştur."""
        # Run bilgilerini al
        df = self.tracker.list_runs()
        
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.tracker.experiment_name} - Deney Raporu</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .best-run {{
            background: #d4edda !important;
            font-weight: bold;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        
        .metric-badge {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            margin: 2px;
        }}
        
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {self.tracker.experiment_name}</h1>
            <p>Deney Raporu - {datetime.now().strftime('%d %B %Y, %H:%M')}</p>
        </header>
        
        <div class="content">
            <!-- Özet İstatistikler -->
            <div class="section">
                <h2>📊 Özet İstatistikler</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Toplam Deneme</h3>
                        <div class="value">{len(df)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Başarılı Deneme</h3>
                        <div class="value">{len(df[df['status'] == 'completed']) if not df.empty else 0}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Toplam Süre</h3>
                        <div class="value">{self._format_total_duration(df)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Takip Edilen Metrikler</h3>
                        <div class="value">{self._count_metrics(df)}</div>
                    </div>
                </div>
            </div>
            
            <!-- Denemeler Tablosu -->
            <div class="section">
                <h2>📋 Tüm Denemeler</h2>
                {self._generate_runs_table(df)}
            </div>
            
            <!-- En İyi Sonuçlar -->
            <div class="section">
                <h2>🏆 En İyi Sonuçlar</h2>
                {self._generate_best_results(df)}
            </div>
        </div>
        
        <div class="footer">
            <p>MLTrackFlow v0.1.0 ile oluşturuldu</p>
            <p>📁 Kayıt Yolu: {self.tracker.experiment_path}</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_runs_table(self, df) -> str:
        """Run tablosunu oluştur."""
        if df.empty:
            return '<div class="no-data">Henüz deneme kaydı bulunmuyor.</div>'
        
        # En iyi run'ı bul (ilk sayısal metriğe göre)
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        best_run_name = None
        if numeric_cols:
            metric_col = [c for c in numeric_cols if c != 'duration_seconds'][0] if len([c for c in numeric_cols if c != 'duration_seconds']) > 0 else None
            if metric_col:
                best_idx = df[metric_col].idxmax()
                best_run_name = df.loc[best_idx, 'run_name']
        
        html = '<table>\n<thead>\n<tr>\n'
        
        # Başlıklar
        for col in df.columns:
            html += f'<th>{col}</th>\n'
        html += '</tr>\n</thead>\n<tbody>\n'
        
        # Satırlar
        for idx, row in df.iterrows():
            row_class = 'best-run' if row['run_name'] == best_run_name else ''
            html += f'<tr class="{row_class}">\n'
            for col in df.columns:
                value = row[col]
                if isinstance(value, float):
                    html += f'<td>{value:.4f}</td>\n'
                else:
                    html += f'<td>{value}</td>\n'
            html += '</tr>\n'
        
        html += '</tbody>\n</table>'
        return html
    
    def _generate_best_results(self, df) -> str:
        """En iyi sonuçları oluştur."""
        if df.empty:
            return '<div class="no-data">Henüz veri bulunmuyor.</div>'
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        metric_cols = [c for c in numeric_cols if c != 'duration_seconds']
        
        if not metric_cols:
            return '<div class="no-data">Metrik bulunamadı.</div>'
        
        html = '<div style="display: grid; gap: 20px;">\n'
        
        for metric in metric_cols:
            best_idx = df[metric].idxmax()
            best_run = df.loc[best_idx, 'run_name']
            best_value = df.loc[best_idx, metric]
            
            html += f'''
            <div style="padding: 20px; background: #f8f9fa; border-left: 4px solid #667eea; border-radius: 5px;">
                <h3 style="color: #667eea; margin-bottom: 10px;">{metric}</h3>
                <p style="font-size: 1.5em; font-weight: bold; color: #333;">{best_value:.4f}</p>
                <p style="color: #666;">🏆 En iyi: {best_run}</p>
            </div>
            '''
        
        html += '</div>'
        return html
    
    def _format_total_duration(self, df) -> str:
        """Toplam süreyi formatla."""
        if df.empty or 'duration_seconds' not in df.columns:
            return "N/A"
        
        total_seconds = df['duration_seconds'].sum()
        
        if total_seconds < 60:
            return f"{total_seconds:.0f}s"
        elif total_seconds < 3600:
            return f"{total_seconds/60:.1f}m"
        else:
            return f"{total_seconds/3600:.1f}h"
    
    def _count_metrics(self, df) -> int:
        """Metrik sayısını say."""
        if df.empty:
            return 0
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        return len([c for c in numeric_cols if c != 'duration_seconds'])


