"""
Komut satırı arayüzü (CLI) modülü.
"""

import argparse
from pathlib import Path


def main():
    """Ana CLI fonksiyonu."""
    parser = argparse.ArgumentParser(
        description='MLTrackFlow - ML Eğitim Süreçlerini İzleme Aracı',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Komutlar')
    
    # init komutu
    init_parser = subparsers.add_parser('init', help='Yeni deney başlat')
    init_parser.add_argument('--name', type=str, required=True, help='Deney adı')
    init_parser.add_argument('--path', type=str, default='./experiments', help='Kayıt yolu')
    
    # list komutu
    list_parser = subparsers.add_parser('list', help='Deneyleri listele')
    list_parser.add_argument('--path', type=str, default='./experiments', help='Deney yolu')
    
    # report komutu
    report_parser = subparsers.add_parser('report', help='Rapor oluştur')
    report_parser.add_argument('--experiment', type=str, required=True, help='Deney adı')
    report_parser.add_argument('--path', type=str, default='./experiments', help='Deney yolu')
    report_parser.add_argument('--output', type=str, help='Çıktı dosya yolu')
    
    # compare komutu
    compare_parser = subparsers.add_parser('compare', help='Run\'ları karşılaştır')
    compare_parser.add_argument('--experiment', type=str, required=True, help='Deney adı')
    compare_parser.add_argument('--path', type=str, default='./experiments', help='Deney yolu')
    compare_parser.add_argument('--runs', type=str, nargs='+', help='Karşılaştırılacak run\'lar')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_experiment(args.name, args.path)
    elif args.command == 'list':
        list_experiments(args.path)
    elif args.command == 'report':
        generate_report(args.experiment, args.path, args.output)
    elif args.command == 'compare':
        compare_runs(args.experiment, args.path, args.runs)
    else:
        parser.print_help()


def init_experiment(name: str, path: str):
    """Yeni deney başlat."""
    from mltrackflow import ExperimentTracker
    
    tracker = ExperimentTracker(experiment_name=name, storage_path=path)
    print(f"\n✅ Deney başlatıldı: {name}")
    print(f"📁 Kayıt yolu: {tracker.experiment_path}\n")


def list_experiments(path: str):
    """Deneyleri listele."""
    exp_path = Path(path)
    
    if not exp_path.exists():
        print(f"❌ Deney yolu bulunamadı: {path}")
        return
    
    experiments = [d for d in exp_path.iterdir() if d.is_dir()]
    
    if not experiments:
        print("Henüz deney yok.")
        return
    
    print("\n📚 Mevcut Deneyler:\n")
    for i, exp in enumerate(experiments, 1):
        print(f"{i}. {exp.name}")
    print()


def generate_report(experiment: str, path: str, output: str = None):
    """Rapor oluştur."""
    from mltrackflow import ExperimentTracker
    
    tracker = ExperimentTracker(experiment_name=experiment, storage_path=path, verbose=False)
    
    report_path = tracker.generate_report(output_path=output)
    print(f"\n✅ Rapor oluşturuldu: {report_path}\n")


def compare_runs(experiment: str, path: str, runs: list = None):
    """Run'ları karşılaştır."""
    from mltrackflow import ExperimentTracker, ModelComparator
    
    tracker = ExperimentTracker(experiment_name=experiment, storage_path=path, verbose=False)
    comparator = ModelComparator(tracker=tracker)
    
    comparator.compare_runs(run_names=runs)
    comparator.print_comparison_table()


if __name__ == '__main__':
    main()


