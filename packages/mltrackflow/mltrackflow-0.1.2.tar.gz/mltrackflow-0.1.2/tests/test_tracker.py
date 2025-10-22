"""
ExperimentTracker için test dosyası.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from mltrackflow import ExperimentTracker


@pytest.fixture
def temp_dir():
    """Geçici test klasörü."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def tracker(temp_dir):
    """Test tracker instance."""
    return ExperimentTracker(
        experiment_name="test_experiment",
        storage_path=temp_dir,
        verbose=False
    )


def test_tracker_initialization(tracker, temp_dir):
    """Tracker'ın doğru başlatıldığını test et."""
    assert tracker.experiment_name == "test_experiment"
    assert tracker.storage_path == Path(temp_dir)
    assert tracker.experiment_path.exists()


def test_start_run(tracker):
    """Run başlatmayı test et."""
    with tracker.start_run("test_run"):
        assert tracker.current_run == "test_run"
        assert tracker.current_run_data is not None


def test_log_params(tracker):
    """Parametre loglamayı test et."""
    with tracker.start_run("test_run"):
        params = {"learning_rate": 0.01, "epochs": 100}
        tracker.log_params(params)
        assert tracker.current_run_data["params"] == params


def test_log_metric(tracker):
    """Metrik loglamayı test et."""
    with tracker.start_run("test_run"):
        tracker.log_metric("accuracy", 0.95)
        assert tracker.current_run_data["metrics"]["accuracy"] == 0.95


def test_log_metrics(tracker):
    """Çoklu metrik loglamayı test et."""
    with tracker.start_run("test_run"):
        metrics = {"accuracy": 0.95, "f1_score": 0.93}
        tracker.log_metrics(metrics)
        assert tracker.current_run_data["metrics"] == metrics


def test_run_finalization(tracker):
    """Run'ın doğru sonlandırıldığını test et."""
    with tracker.start_run("test_run"):
        tracker.log_metric("accuracy", 0.95)
    
    assert tracker.current_run is None
    assert "test_run" in tracker.metadata["runs"]
    assert tracker.metadata["runs"]["test_run"]["status"] == "completed"


def test_list_runs(tracker):
    """Run listelemeyi test et."""
    with tracker.start_run("run_1"):
        tracker.log_metric("accuracy", 0.85)
    
    with tracker.start_run("run_2"):
        tracker.log_metric("accuracy", 0.90)
    
    df = tracker.list_runs()
    assert len(df) == 2
    assert "run_1" in df["run_name"].values
    assert "run_2" in df["run_name"].values


def test_get_best_run(tracker):
    """En iyi run'ı bulma testi."""
    with tracker.start_run("run_1"):
        tracker.log_metric("accuracy", 0.85)
    
    with tracker.start_run("run_2"):
        tracker.log_metric("accuracy", 0.90)
    
    with tracker.start_run("run_3"):
        tracker.log_metric("accuracy", 0.88)
    
    best_run = tracker.get_best_run(metric="accuracy", maximize=True)
    assert best_run == "run_2"


def test_save_and_load_model(tracker):
    """Model kaydetme ve yükleme testi."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris
    
    # Model eğit
    data = load_iris()
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(data.data[:100], data.target[:100])
    
    # Kaydet
    with tracker.start_run("model_test"):
        tracker.save_model(model, "test_model")
    
    # Yükle
    loaded_model = tracker.load_model("model_test", "test_model")
    
    # Tahminleri karşılaştır
    pred1 = model.predict(data.data[100:110])
    pred2 = loaded_model.predict(data.data[100:110])
    
    assert (pred1 == pred2).all()


def test_log_model_metrics(tracker):
    """Otomatik metrik loglama testi."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split
    
    # Veri hazırla
    data = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.2, random_state=42
    )
    
    # Model eğit
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Metrikleri otomatik kaydet
    with tracker.start_run("auto_metrics_test"):
        tracker.log_model_metrics(model, X_test, y_test, task_type="classification")
        
        # Metriklerin kaydedildiğini kontrol et
        assert "accuracy" in tracker.current_run_data["metrics"]
        assert "precision" in tracker.current_run_data["metrics"]
        assert "recall" in tracker.current_run_data["metrics"]
        assert "f1_score" in tracker.current_run_data["metrics"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


