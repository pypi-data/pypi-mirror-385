# MLTrackFlow 🚀

[![PyPI version](https://img.shields.io/pypi/v/mltrackflow.svg)](https://pypi.org/project/mltrackflow/)
[![Python](https://img.shields.io/pypi/pyversions/mltrackflow.svg)](https://pypi.org/project/mltrackflow/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/mltrackflow.svg)](https://pypi.org/project/mltrackflow/)

**Makine Öğrenimi Eğitim Süreçlerini Şeffaf ve İzlenebilir Hale Getiren Python Kütüphanesi**

MLTrackFlow, ML model geliştirme sürecinizi adım adım izlemenize, kayıt altına almanıza ve görselleştirmenize olanak tanıyan **kullanıcı dostu** bir Python paketidir.

## ✨ Neden MLTrackFlow?

### 🎯 Tek Satırda Başlayın
```python
from mltrackflow import ExperimentTracker

tracker = ExperimentTracker(experiment_name="my_project")
with tracker.start_run("first_experiment"):
    tracker.log_model_metrics(model, X_test, y_test)  # Otomatik!
```

### 🌟 Temel Özellikler

- **🎓 Yeni Başlayanlar İçin**: Basit API, otomatik loglama, bol örnek
- **📊 Otomatik Metrik Takibi**: Accuracy, precision, recall, F1 otomatik hesaplanır
- **🔄 Pipeline Yönetimi**: Veri hazırlıktan modele kadar tüm adımları organize edin
- **📈 Zengin Görselleştirme**: Confusion matrix, learning curves, feature importance
- **🏆 Model Karşılaştırma**: Farklı modelleri kolayca kıyaslayın
- **📄 HTML Raporları**: Tek tıkla profesyonel raporlar
- **💾 Model Versiyonlama**: Tüm modellerinizi organize edin
- **🔒 Veri İzleme**: Otomatik veri hash'leme ile değişiklikleri takip edin

## 🚀 Hızlı Başlangıç

### Kurulum

```bash
pip install mltrackflow
```

### İlk Deneyiniz (60 saniye!)

```python
from mltrackflow import ExperimentTracker
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Veriyi hazırla
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# Tracker'ı başlat
tracker = ExperimentTracker(experiment_name="iris_demo")

# Model eğit ve kaydet
with tracker.start_run("random_forest"):
    # Parametreleri kaydet
    tracker.log_params({"n_estimators": 100, "max_depth": 5})
    
    # Model eğit
    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X_train, y_train)
    
    # Metrikleri OTOMATIK hesapla ve kaydet
    tracker.log_model_metrics(model, X_test, y_test)
    
    # Modeli kaydet
    tracker.save_model(model, "my_model")

# HTML rapor oluştur
tracker.generate_report()
print("✅ Rapor oluşturuldu: experiments/iris_demo/experiment_report.html")
```

**Çıktı:**
```
🚀 Run başlatıldı: random_forest
📊 Metrik kaydedildi: accuracy = 0.9667
📊 Metrik kaydedildi: precision = 0.9722
📊 Metrik kaydedildi: recall = 0.9667
📊 Metrik kaydedildi: f1_score = 0.9667
✅ Run tamamlandı: random_forest
```

## 📚 Özellikler Detaylı

### 1️⃣ Pipeline ile Modüler İş Akışı

```python
from mltrackflow import MLPipeline, PipelineStep
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Pipeline oluştur
pipeline = MLPipeline(name="data_pipeline", tracker=tracker)

# Adımları ekle
pipeline.add_step(PipelineStep(name="scaler", transformer=StandardScaler()))
pipeline.add_step(PipelineStep(name="pca", transformer=PCA(n_components=2)))
pipeline.add_step(PipelineStep(name="model", model=RandomForestClassifier()))

# Eğit
with tracker.start_run("pipeline_demo"):
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

# Görselleştir
pipeline.visualize_steps(output_path="pipeline.png")
```

### 2️⃣ Model Karşılaştırma

```python
from mltrackflow import ModelComparator

# Farklı modelleri dene
models = {
    "rf": RandomForestClassifier(n_estimators=100),
    "svm": SVC(kernel='rbf'),
    "logistic": LogisticRegression(),
}

for name, model in models.items():
    with tracker.start_run(name):
        model.fit(X_train, y_train)
        tracker.log_model_metrics(model, X_test, y_test)

# Karşılaştır
comparator = ModelComparator(tracker=tracker)
comparator.compare_runs()
comparator.print_comparison_table()

# En iyiyi bul
best = comparator.get_best_model(metric="accuracy", maximize=True)
print(f"🏆 En iyi model: {best}")
```

### 3️⃣ Görselleştirme

```python
from mltrackflow import Visualizer

viz = Visualizer(tracker=tracker)

# Confusion matrix
viz.plot_confusion_matrix(y_test, predictions)

# Feature importance
viz.plot_feature_importance(model, feature_names)

# Model karşılaştırma
viz.plot_metrics_comparison(
    run_names=["rf", "svm", "logistic"],
    metrics=["accuracy", "f1_score"]
)
```

## 🎨 Ne Görürsünüz?

MLTrackFlow ile her deneyde:

✅ **Otomatik Kayıt**: Parametreler, metrikler, modeller  
✅ **Zaman Damgası**: Her işlem zamanlanır  
✅ **Karşılaştırma Tablosu**: Tüm denemeleri yan yana görün  
✅ **HTML Rapor**: Profesyonel, paylaşılabilir raporlar  
✅ **Grafikler**: Confusion matrix, learning curves, feature importance  
✅ **En İyi Model**: Otomatik seçim

## 💡 Komut Satırı Kullanımı

```bash
# Yeni deney başlat
mltrackflow init --name my_experiment

# Deneyleri listele
mltrackflow list

# Rapor oluştur
mltrackflow report --experiment iris_demo

# Modelleri karşılaştır
mltrackflow compare --experiment iris_demo --runs rf svm logistic
```

## 🆚 Diğer Araçlarla Karşılaştırma

| Özellik | MLflow | W&B | **MLTrackFlow** |
|---------|--------|-----|-----------------|
| Kurulum | Karmaşık | Kayıt gerekli | `pip install` ✅ |
| Öğrenme Eğrisi | Orta | Orta | **Kolay** 🎓 |
| Lokal Çalışma | ✅ | Kısıtlı | **✅** |
| Pipeline Desteği | ❌ | ❌ | **✅** |
| Otomatik Metrikler | Kısıtlı | Kısıtlı | **Tam Otomatik** 🤖 |
| Türkçe Dokümantasyon | ❌ | ❌ | **✅** 🇹🇷 |
| Yeni Başlayanlar İçin | ⚠️ | ⚠️ | **✅** |

## 📖 Dokümantasyon

- [Hızlı Başlangıç Rehberi](https://github.com/yourusername/mltrackflow/blob/main/QUICKSTART.md)
- [API Referansı](https://github.com/yourusername/mltrackflow/tree/main/mltrackflow)
- [Örnek Projeler](https://github.com/yourusername/mltrackflow/tree/main/examples)
- [PyPI Yayınlama](https://github.com/yourusername/mltrackflow/blob/main/PYPI_YAYINLAMA.md)

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen [CONTRIBUTING.md](https://github.com/yourusername/mltrackflow/blob/main/CONTRIBUTING.md) dosyasına bakın.

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

MLTrackFlow, makine öğrenimi topluluğunun ihtiyaçlarına cevap vermek ve eğitim süreçlerini daha şeffaf kılmak amacıyla geliştirilmiştir.

---

**Hızlı Bağlantılar:**
[GitHub](https://github.com/yourusername/mltrackflow) • 
[PyPI](https://pypi.org/project/mltrackflow/) • 
[Örnekler](https://github.com/yourusername/mltrackflow/tree/main/examples) • 
[Sorunlar](https://github.com/yourusername/mltrackflow/issues)

**Yıldız vermeyi unutmayın! ⭐**
