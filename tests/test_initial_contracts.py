"""
test_initial_contracts.py
Memeriksa kelengkapan struktur repositori, berkas dokumentasi,
dan kepatuhan terhadap Gerbang G0 (Langkah 0).
"""

from pathlib import Path


def test_repository_folders_exist():
    """Memastikan semua folder standar PRD §8 sudah terbentuk."""
    repo_root = Path(__file__).resolve().parent.parent
    expected_dirs = [
        "docs",
        "data/raw",
        "data/processed",
        "sql",
        "src",
        "tests",
        "notebooks",
        "config",
        "experiments",
        "artifacts",
        "reports",
        "app",
    ]
    for rel_path in expected_dirs:
        dir_path = repo_root / rel_path
        assert dir_path.is_dir(), f"Folder {rel_path} harus ada sesuai PRD §8."


def test_gate_g0_documents_exist():
    """Memastikan dokumen prasyarat Gerbang G0 sudah tersedia."""
    repo_root = Path(__file__).resolve().parent.parent
    expected_files = [
        "docs/PRD_WMFB_Olist.md",
        "docs/problem_statement.md",
        "docs/CATATAN_BELAJAR.md",
        "config/analysis_plan.md",
        "experiments/PROGRESS.md",
        "experiments/decision_log.md",
        "experiments/experiment_log.md",
        ".gitignore",
    ]
    for rel_path in expected_files:
        file_path = repo_root / rel_path
        assert file_path.is_file(), f"Berkas {rel_path} harus ada sebelum modeling dimulai."


def test_locked_definitions_in_analysis_plan():
    """Memastikan definisi kunci operasional bisnis ada di config/analysis_plan.md."""
    repo_root = Path(__file__).resolve().parent.parent
    plan_path = repo_root / "config/analysis_plan.md"
    content = plan_path.read_text(encoding="utf-8")

    # Memastikan definisi operasional utama dikunci
    assert "Pesanan Terlambat" in content, "Definisi 'Pesanan Terlambat' wajib dikunci."
    assert "Ulasan Buruk" in content, "Definisi 'Ulasan Buruk' wajib dikunci."
    assert "WAPE" in content, "Metrik WAPE wajib tercantum."
    assert "Lift" in content, "Metrik Lift wajib tercantum."
