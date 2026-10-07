"""
tests/test_time_split.py
Tes Otomatis 2: Pembagian Waktu & Integritas Holdout (PRD §3.1, §4.2 #2)
Memeriksa bahwa:
1. Tidak ada tumpang tindih waktu antara data development (EDA/latih) dan holdout.
2. Seluruh baris holdout strictly berada di masa depan relatif terhadap development.
3. Checksum SHA-256 holdout cocok persis dengan segel di experiments/holdout_checksum.sha256.
"""

import hashlib
from pathlib import Path
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def paths():
    repo_root = Path(__file__).resolve().parent.parent
    return {
        "dev_file": repo_root / "data" / "processed" / "dev_orders.parquet",
        "holdout_file": repo_root / "data" / "processed" / "holdout_orders.parquet",
        "checksum_file": repo_root / "experiments" / "holdout_checksum.sha256",
    }


def test_holdout_files_exist(paths):
    """Memastikan berkas dev_orders dan holdout_orders telah dibuat."""
    assert paths["dev_file"].exists(), "Berkas dev_orders.parquet belum dibuat."
    assert paths["holdout_file"].exists(), "Berkas holdout_orders.parquet belum dibuat."
    assert paths["checksum_file"].exists(), "Berkas segel holdout_checksum.sha256 belum dibuat."


def test_no_temporal_overlap(paths):
    """Memastikan tidak ada tumpang tindih waktu: max(dev) < min(holdout)."""
    dev_df = pd.read_parquet(paths["dev_file"], columns=["order_purchase_timestamp"])
    holdout_df = pd.read_parquet(paths["holdout_file"], columns=["order_purchase_timestamp"])

    max_dev_time = pd.to_datetime(dev_df["order_purchase_timestamp"]).max()
    min_holdout_time = pd.to_datetime(holdout_df["order_purchase_timestamp"]).min()

    assert max_dev_time < min_holdout_time, (
        f"Terjadi kebocoran waktu! max dev: {max_dev_time} >= min holdout: {min_holdout_time}"
    )


def test_holdout_checksum_matches(paths):
    """Memastikan berkas holdout tidak pernah diubah atau disentuh sejak disegel."""
    sha256 = hashlib.sha256()
    with open(paths["holdout_file"], "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    actual_checksum = sha256.hexdigest()

    expected_checksum = paths["checksum_file"].read_text(encoding="utf-8").split()[0].strip()
    assert actual_checksum == expected_checksum, (
        f"Segel integritas rusak! Checksum aktual: {actual_checksum} != tersimpan: {expected_checksum}"
    )
