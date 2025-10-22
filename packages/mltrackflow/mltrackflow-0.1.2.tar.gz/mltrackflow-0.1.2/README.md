# MLTrackFlow 🚀

[![PyPI version](https://img.shields.io/pypi/v/mltrackflow.svg)](https://pypi.org/project/mltrackflow/)
[![Python](https://img.shields.io/pypi/pyversions/mltrackflow.svg)](https://pypi.org/project/mltrackflow/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/mltrackflow.svg)](https://pypi.org/project/mltrackflow/)

**A User-Friendly Python Library for Making Machine Learning Training Processes Transparent and Traceable**

MLTrackFlow is a **beginner-friendly** Python package that enables you to track, record, and visualize your ML model development process step by step.

---

## 🌟 Why MLTrackFlow?

### 🎯 Get Started in One Line
```python
from mltrackflow import ExperimentTracker

tracker = ExperimentTracker(experiment_name="my_project")
with tracker.start_run("first_experiment"):
    tracker.log_model_metrics(model, X_test, y_test)  # Automatic!
```

### ✨ Key Features

- **🎓 Perfect for Beginners**: Simple API, automatic logging, plenty of examples
- **📊 Automatic Metric Tracking**: Accuracy, precision, recall, F1 calculated automatically
- **🔄 Pipeline Management**: Organize all steps from data preparation to model
- **📈 Rich Visualization**: Confusion matrix, learning curves, feature importance
- **🏆 Model Comparison**: Easily compare different models
- **📄 HTML Reports**: Professional reports with one click
- **💾 Model Versioning**: Organize all your models
- **🔒 Data Tracking**: Track changes with automatic data hashing

## 🚀 Quick Start

### Installation

```bash
pip install mltrackflow
```

### Your First Experiment (60 seconds!)

```python
from mltrackflow import ExperimentTracker
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Prepare data
data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# Start tracker
tracker = ExperimentTracker(experiment_name="iris_demo")

# Train and log
with tracker.start_run("random_forest"):
    # Log parameters
    tracker.log_params({"n_estimators": 100, "max_depth": 5})
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=5)
    model.fit(X_train, y_train)
    
    # Automatically calculate and log metrics
    tracker.log_model_metrics(model, X_test, y_test)
    
    # Save model
    tracker.save_model(model, "my_model")

# Generate HTML report
tracker.generate_report()
print("✅ Report created: experiments/iris_demo/experiment_report.html")
```

**Output:**
```
🚀 Run started: random_forest
📊 Metric logged: accuracy = 0.9667
📊 Metric logged: precision = 0.9722
📊 Metric logged: recall = 0.9667
📊 Metric logged: f1_score = 0.9667
✅ Run completed: random_forest
```

## 📚 Feature Details

### 1️⃣ Modular Workflow with Pipeline

```python
from mltrackflow import MLPipeline, PipelineStep
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Create pipeline
pipeline = MLPipeline(name="data_pipeline", tracker=tracker)

# Add steps
pipeline.add_step(PipelineStep(name="scaler", transformer=StandardScaler()))
pipeline.add_step(PipelineStep(name="pca", transformer=PCA(n_components=2)))
pipeline.add_step(PipelineStep(name="model", model=RandomForestClassifier()))

# Train
with tracker.start_run("pipeline_demo"):
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

# Visualize
pipeline.visualize_steps(output_path="pipeline.png")
```

### 2️⃣ Model Comparison

```python
from mltrackflow import ModelComparator

# Try different models
models = {
    "rf": RandomForestClassifier(n_estimators=100),
    "svm": SVC(kernel='rbf'),
    "logistic": LogisticRegression(),
}

for name, model in models.items():
    with tracker.start_run(name):
        model.fit(X_train, y_train)
        tracker.log_model_metrics(model, X_test, y_test)

# Compare
comparator = ModelComparator(tracker=tracker)
comparator.compare_runs()
comparator.print_comparison_table()

# Find best
best = comparator.get_best_model(metric="accuracy", maximize=True)
print(f"🏆 Best model: {best}")
```

### 3️⃣ Visualization

```python
from mltrackflow import Visualizer

viz = Visualizer(tracker=tracker)

# Confusion matrix
viz.plot_confusion_matrix(y_test, predictions)

# Feature importance
viz.plot_feature_importance(model, feature_names)

# Model comparison
viz.plot_metrics_comparison(
    run_names=["rf", "svm", "logistic"],
    metrics=["accuracy", "f1_score"]
)
```

## 🆚 Comparison with Other Tools

| Feature | MLflow | W&B | **MLTrackFlow** |
|---------|--------|-----|-----------------|
| Installation | Complex | Registration required | `pip install` ✅ |
| Learning Curve | Medium | Medium | **Easy** 🎓 |
| Local Execution | ✅ | Limited | **✅** |
| Pipeline Support | ❌ | ❌ | **✅** |
| Auto Metrics | Limited | Limited | **Fully Automatic** 🤖 |
| Beginner Friendly | ⚠️ | ⚠️ | **✅** |

## 💡 Command Line Usage

```bash
# Start new experiment
mltrackflow init --name my_experiment

# List experiments
mltrackflow list

# Generate report
mltrackflow report --experiment iris_demo

# Compare models
mltrackflow compare --experiment iris_demo --runs rf svm logistic
```

## 📖 Documentation

- [Quick Start Guide](https://github.com/yourusername/mltrackflow/blob/main/QUICKSTART.md)
- [API Reference](https://github.com/yourusername/mltrackflow/tree/main/mltrackflow)
- [Example Projects](https://github.com/yourusername/mltrackflow/tree/main/examples)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/yourusername/mltrackflow/blob/main/CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

# 🇹🇷 Türkçe Açıklama

**Makine Öğrenimi Eğitim Süreçlerini Şeffaf ve İzlenebilir Hale Getiren Kullanıcı Dostu Python Kütüphanesi**

MLTrackFlow, ML model geliştirme sürecinizi adım adım izlemenize, kayıt altına almanıza ve görselleştirmenize olanak tanıyan **yeni başlayanlar için ideal** bir Python paketidir.

## 🌟 Neden MLTrackFlow?

- **🎓 Yeni Başlayanlar İçin**: Basit API, otomatik loglama
- **📊 Otomatik Metrik Takibi**: Tüm metrikler otomatik hesaplanır
- **🔄 Pipeline Yönetimi**: Veri hazırlıktan modele kadar tüm adımları organize edin
- **📈 Zengin Görselleştirme**: Karmaşıklık matrisi, öğrenme eğrileri
- **🏆 Model Karşılaştırma**: Farklı modelleri kolayca kıyaslayın
- **📄 HTML Raporları**: Tek tıkla profesyonel raporlar

## 🚀 Kurulum ve Kullanım

```bash
pip install mltrackflow
```

```python
from mltrackflow import ExperimentTracker
from sklearn.ensemble import RandomForestClassifier

# Tracker başlat
tracker = ExperimentTracker(experiment_name="proje_adi")

# Model eğit ve kaydet
with tracker.start_run("deneme_1"):
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Metrikleri otomatik kaydet
    tracker.log_model_metrics(model, X_test, y_test)
    
    # Modeli kaydet
    tracker.save_model(model, "modelim")

# HTML rapor oluştur
tracker.generate_report()
```

## 📚 Özellikler

### Pipeline ile Modüler İş Akışı

```python
from mltrackflow import MLPipeline, PipelineStep
from sklearn.preprocessing import StandardScaler

pipeline = MLPipeline(name="veri_pipeline")
pipeline.add_step(PipelineStep(name="olcekleme", transformer=StandardScaler()))
pipeline.add_step(PipelineStep(name="model", model=RandomForestClassifier()))

pipeline.fit(X_train, y_train)
pipeline.visualize_steps()  # Pipeline'ı görselleştir
```

### Model Karşılaştırma

```python
from mltrackflow import ModelComparator

# Farklı modelleri dene
for model_name, model in models.items():
    with tracker.start_run(model_name):
        model.fit(X_train, y_train)
        tracker.log_model_metrics(model, X_test, y_test)

# Karşılaştır
comparator = ModelComparator(tracker=tracker)
comparator.compare_runs()
best = comparator.get_best_model(metric="accuracy")
```

### Görselleştirme

```python
from mltrackflow import Visualizer

viz = Visualizer(tracker=tracker)
viz.plot_confusion_matrix(y_test, predictions)
viz.plot_feature_importance(model, feature_names)
viz.plot_metrics_comparison(["model1", "model2"])
```

## 💡 Komut Satırı

```bash
# Yeni deney başlat
mltrackflow init --name proje_adi

# Deneyleri listele
mltrackflow list

# Rapor oluştur
mltrackflow report --experiment proje_adi
```

## 🎯 Ne Görürsünüz?

Her deneyde:
- ✅ Otomatik parametre ve metrik kaydı
- ✅ Zaman damgası
- ✅ Karşılaştırma tablosu
- ✅ HTML rapor (grafiklerle)
- ✅ En iyi model otomatik seçimi

## 📖 Dokümantasyon

- [Hızlı Başlangıç Rehberi (Türkçe)](https://github.com/yourusername/mltrackflow/blob/main/QUICKSTART.md)
- [Örnek Projeler](https://github.com/yourusername/mltrackflow/tree/main/examples)
- [API Dökümanı](https://github.com/yourusername/mltrackflow/tree/main/mltrackflow)

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! [CONTRIBUTING.md](https://github.com/yourusername/mltrackflow/blob/main/CONTRIBUTING.md) dosyasına bakın.

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

**Quick Links:**
[GitHub](https://github.com/yourusername/mltrackflow) • 
[PyPI](https://pypi.org/project/mltrackflow/) • 
[Examples](https://github.com/yourusername/mltrackflow/tree/main/examples) • 
[Issues](https://github.com/yourusername/mltrackflow/issues)

**Don't forget to star! ⭐ / Yıldız vermeyi unutmayın! ⭐**
