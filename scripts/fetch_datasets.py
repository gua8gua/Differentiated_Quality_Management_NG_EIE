#!/usr/bin/env python3
"""
Download open-source benchmark datasets for the NG-EIE quality management project.

Usage:
    python scripts/fetch_datasets.py
    python scripts/fetch_datasets.py --only secom,cwru,mcdm
    python scripts/fetch_datasets.py --max-gb 20
"""

from __future__ import annotations

import os
import argparse
import csv
import hashlib
import json
import random
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
MANIFEST_PATH = DATASETS / "manifest.json"
TMP_DIR = Path(__file__).resolve().parent / ".download_tmp"

USER_AGENT = "NG-EIE-Dataset-Fetcher/1.0 (research; +local)"


def log(msg: str) -> None:
    print(msg, flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def total_datasets_size() -> int:
    return sum(dir_size(DATASETS / d) for d in DATASET_DIRS.values() if (DATASETS / d).exists())


def download_url(url: str, dest: Path, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            dest.write_bytes(data)
            return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            log(f"  retry {attempt}/{retries} failed: {exc}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"download failed: {url} -> {last_err}")


def download_url_stream(url: str, dest: Path, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                with dest.open("wb") as out:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        out.write(chunk)
            return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            log(f"  retry {attempt}/{retries} failed: {exc}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"download failed: {url} -> {last_err}")


def run_cmd(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def record_entry(manifest: dict[str, Any], entry: dict[str, Any]) -> None:
    manifest["entries"] = [e for e in manifest["entries"] if e.get("id") != entry["id"]]
    manifest["entries"].append(entry)


def ok_entry(entry_id: str, name: str, out_dir: Path, **extra: Any) -> dict[str, Any]:
    size = dir_size(out_dir)
    return {
        "id": entry_id,
        "name": name,
        "path": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
        "status": "ok",
        "bytes": size,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **extra,
    }


def fail_entry(entry_id: str, name: str, out_dir: Path, error: str, **extra: Any) -> dict[str, Any]:
    return {
        "id": entry_id,
        "name": name,
        "path": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
        "status": "failed",
        "bytes": dir_size(out_dir),
        "error": error,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **extra,
    }


DATASET_DIRS = {
    "secom": "01_tabular_secom",
    "cwru": "02_phm_cwru",
    "cmapss": "03_phm_nasa_cmapss",
    "mvtec": "04_vision_mvtec_bottle",
    "hai": "05_iot_hai",
    "mimii": "06_acoustic_mimii_toy",
    "iof": "07_semantic_iof",
    "mcdm": "08_synthetic_mcdm",
    "mfg009": "09_iiot_mfg009_sample",
    "rag_sample": "10_text_rag_sample",
}


def fetch_secom(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["secom"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "secom"
    try:
        zip_path = TMP_DIR / "secom.zip"
        download_url("https://archive.ics.uci.edu/static/public/179/secom.zip", zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(out)
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "UCI SECOM",
                out,
                url="https://archive.ics.uci.edu/dataset/179/secom",
                license="Public (UCI)",
            ),
        )
        log(f"[ok] SECOM -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "UCI SECOM", out, str(exc)))
        log(f"[fail] SECOM: {exc}")


def fetch_cwru(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["cwru"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "cwru"
    files = {
        "97.mat": "https://engineering.case.edu/sites/default/files/97.mat",
        "105.mat": "https://engineering.case.edu/sites/default/files/105.mat",
        "118.mat": "https://engineering.case.edu/sites/default/files/118.mat",
    }
    try:
        downloaded = 0
        for name, url in files.items():
            dest = out / name
            try:
                download_url_stream(url, dest)
                downloaded += 1
            except Exception as exc:  # noqa: BLE001
                log(f"  skip {name}: {exc}")
        if downloaded == 0:
            raise RuntimeError("no CWRU .mat files downloaded from Case site")
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "CWRU Bearing subset",
                out,
                url="https://engineering.case.edu/bearingdatacenter",
                license="Research use (CWRU)",
                note=f"{downloaded}/{len(files)} mat files",
            ),
        )
        log(f"[ok] CWRU ({downloaded} files) -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "CWRU Bearing subset", out, str(exc)))
        log(f"[fail] CWRU: {exc}")


def hf_snapshot(repo_id: str, local_dir: Path, repo_type: str | None = None, allow_patterns: list[str] | None = None) -> None:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("pip install huggingface_hub") from exc
    kwargs: dict[str, Any] = {"repo_id": repo_id, "local_dir": str(local_dir)}
    if repo_type:
        kwargs["repo_type"] = repo_type
    if allow_patterns:
        kwargs["allow_patterns"] = allow_patterns
    snapshot_download(**kwargs)


def phmd_download_cmapss(out: Path) -> None:
    phmd_root = ROOT / "projects" / "phmd"
    if not phmd_root.exists():
        raise RuntimeError("projects/phmd not cloned; run clone_projects.ps1 first")
    cache = TMP_DIR / "phmd_cache"
    cache.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(phmd_root) + os.pathsep + env.get("PYTHONPATH", "")
    script = """
import shutil
from pathlib import Path
from phmd.download import download
cache = Path(r"%s")
download("CMAPSS", cache_dir=str(cache), unzip=True)
""" % str(cache).replace("\\", "\\\\")
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, env=env, cwd=str(phmd_root))
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    train_dir = cache / "datasets" / "CMAPSS" / "train"
    test_dir = cache / "datasets" / "CMAPSS" / "test"
    fd = out / "FD001"
    fd.mkdir(parents=True, exist_ok=True)
    copied = False
    for src_dir in (train_dir, test_dir):
        if not src_dir.exists():
            continue
        for f in src_dir.glob("*FD001*"):
            shutil.copy2(f, fd / f.name)
            copied = True
    if not copied:
        raise RuntimeError("CMAPSS downloaded but FD001 files not found")


def fetch_cmapss(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["cmapss"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "cmapss"
    try:
        phmd_download_cmapss(out)
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "NASA C-MAPSS FD001 (via phmd)",
                out,
                url="https://github.com/dasolma/phmd",
                license="Public (NASA)",
            ),
        )
        log(f"[ok] C-MAPSS -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "NASA C-MAPSS", out, str(exc)))
        log(f"[fail] C-MAPSS: {exc}")


def generate_synthetic_mvtec_bottle(out: Path) -> None:
    """Minimal MVTec-like folder layout when official mirrors are unavailable."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("pip install pillow numpy for synthetic MVTec fallback") from exc

    root = out / "bottle"
    splits = {
        root / "train" / "good": 8,
        root / "test" / "good": 4,
        root / "test" / "broken_large": 4,
    }
    for folder, count in splits.items():
        folder.mkdir(parents=True, exist_ok=True)
        for i in range(count):
            arr = np.random.randint(180, 220, (256, 256, 3), dtype=np.uint8)
            if "broken" in str(folder):
                arr[100:150, 100:150] = [40, 40, 200]
            Image.fromarray(arr).save(folder / f"{folder.parent.name}_{i:03d}.png")
    gt_dir = root / "ground_truth" / "broken_large"
    gt_dir.mkdir(parents=True, exist_ok=True)
    for i in range(4):
        mask = np.zeros((256, 256), dtype=np.uint8)
        mask[100:150, 100:150] = 255
        Image.fromarray(mask).save(gt_dir / f"broken_large_{i:03d}_mask.png")
    (out / "README.txt").write_text(
        "Synthetic MVTec AD bottle layout (official download URLs currently 404).\n"
        "Replace with real MVTec AD bottle when available:\n"
        "https://www.mvtec.com/company/research/datasets/mvtec-ad\n",
        encoding="utf-8",
    )


def extract_mvtec_bottle(tar_path: Path, out: Path) -> None:
    bottle_root = out / "bottle"
    bottle_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "r:xz") as tf:
        for member in tf.getmembers():
            if "/bottle/" not in member.name and not member.name.startswith("bottle/"):
                continue
            member.name = member.name.split("bottle/", 1)[-1] if "bottle/" in member.name else member.name
            if not member.name or member.name.endswith("/"):
                continue
            target = bottle_root / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            src = tf.extractfile(member)
            if src is None:
                continue
            with target.open("wb") as dst:
                shutil.copyfileobj(src, dst)


def fetch_mvtec_bottle(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["mvtec"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "mvtec"
    mvtec_url = (
        "https://www.mydrive.ch/shares/38536/3830184030e49fe74747669442f0f283/"
        "download/420938113-1629960298/mvtec_anomaly_detection.tar.xz"
    )
    try:
        tar_path = TMP_DIR / "mvtec_anomaly_detection.tar.xz"
        if not tar_path.exists() or tar_path.stat().st_size < 1_000_000:
            log("  downloading MVTec AD archive (~4.9GB), extracting bottle/ only...")
            download_url_stream(mvtec_url, tar_path)
        extract_mvtec_bottle(tar_path, out)
        if dir_size(out) < 1000:
            raise RuntimeError("bottle extraction produced no files")
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "MVTec AD bottle",
                out,
                url=mvtec_url,
                license="CC BY-NC-SA 4.0 (non-commercial research)",
                note="full tar cached under scripts/.download_tmp",
            ),
        )
        log(f"[ok] MVTec bottle -> {out}")
    except Exception as exc:  # noqa: BLE001
        try:
            generate_synthetic_mvtec_bottle(out)
            record_entry(
                manifest,
                ok_entry(
                    entry_id,
                    "MVTec AD bottle (synthetic fallback)",
                    out,
                    url="local-synthetic",
                    license="Project internal (replace with CC BY-NC-SA MVTec AD)",
                    note=f"official download failed: {exc}",
                ),
            )
            log(f"[ok] MVTec synthetic fallback -> {out}")
        except Exception as exc2:  # noqa: BLE001
            record_entry(
                manifest,
                fail_entry(
                    entry_id,
                    "MVTec AD bottle",
                    out,
                    str(exc2),
                    manual="https://www.mvtec.com/company/research/datasets/mvtec-ad",
                ),
            )
            log(f"[fail] MVTec bottle: {exc2}")


def generate_synthetic_iot(out: Path) -> None:
    """Fallback when HAI Git LFS quota is unavailable."""
    out.mkdir(parents=True, exist_ok=True)
    random.seed(42)
    tags = ["OPC.Temperature", "OPC.Pressure", "OPC.Flow", "OPC.Level", "OPC.Voltage"]
    rows = []
    t0 = 1_700_000_000
    for i in range(5000):
        ts = t0 + i
        attack = 1 if 3500 <= i < 3600 else 0
        for tag in tags:
            base = hash(tag) % 100
            val = base + random.gauss(0, 1) + (5.0 if attack else 0.0)
            rows.append((ts, tag, round(val, 4), attack))
    csv_path = out / "synthetic_opc_timeseries.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "tag", "value", "attack"])
        w.writerows(rows)
    (out / "README.txt").write_text(
        "Synthetic OPC-like IoT stream (HAI Git LFS unavailable).\n"
        "Replace with full HAI from https://github.com/icsdataset/hai when LFS accessible.\n",
        encoding="utf-8",
    )


def fetch_hai(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["hai"]
    entry_id = "hai"
    repo_dir = TMP_DIR / f"hai_repo_{int(time.time())}"
    try:
        if repo_dir.exists():
            shutil.rmtree(repo_dir, ignore_errors=True)
        result = run_cmd(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--filter=blob:none",
                "--sparse",
                "https://github.com/icsdataset/hai.git",
                str(repo_dir),
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        # Small subset: one train + one test split from latest bundle
        sparse = run_cmd(
            ["git", "sparse-checkout", "set", "hai-22.04/train1.csv.gz", "hai-22.04/test1.csv.gz"],
            cwd=repo_dir,
        )
        if sparse.returncode != 0:
            run_cmd(
                ["git", "sparse-checkout", "set", "hai-21.03/train1.csv.gz", "hai-21.03/test1.csv.gz"],
                cwd=repo_dir,
            )
        run_cmd(["git", "checkout"], cwd=repo_dir)
        out.mkdir(parents=True, exist_ok=True)
        copied = 0
        for gz in repo_dir.rglob("*.csv.gz"):
            dest = out / gz.relative_to(repo_dir)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(gz, dest)
            copied += 1
        if copied == 0:
            raise RuntimeError("HAI sparse checkout found no csv.gz files")
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "HAI ICS subset",
                out,
                url="https://github.com/icsdataset/hai",
                license="Research use",
                note=f"{copied} csv.gz files",
            ),
        )
        log(f"[ok] HAI -> {out}")
    except Exception as exc:  # noqa: BLE001
        out.mkdir(parents=True, exist_ok=True)
        try:
            generate_synthetic_iot(out)
            record_entry(
                manifest,
                ok_entry(
                    entry_id,
                    "HAI ICS (synthetic fallback)",
                    out,
                    url="local-synthetic",
                    license="Project internal",
                    note=f"HAI LFS unavailable: {exc}",
                ),
            )
            log(f"[ok] HAI synthetic fallback -> {out}")
        except Exception as exc2:  # noqa: BLE001
            record_entry(manifest, fail_entry(entry_id, "HAI ICS subset", out, str(exc2)))
            log(f"[fail] HAI: {exc2}")


def fetch_mimii_toy(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["mimii"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "mimii"
    # MIMII single-machine bundle (0 dB valve, ~200MB)
    urls = [
        "https://zenodo.org/records/3384388/files/0_dB_valve.zip?download=1",
        "https://zenodo.org/records/3384388/files/0_dB_pump.zip?download=1",
    ]
    try:
        zip_path = TMP_DIR / "mimii_dev.zip"
        last_err: Exception | None = None
        for u in urls:
            try:
                download_url_stream(u, zip_path)
                last_err = None
                break
            except Exception as exc:  # noqa: BLE001
                last_err = exc
        if last_err:
            raise last_err
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(out)
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "MIMII dev toy subset",
                out,
                url=urls[0],
                license="CC BY-SA 4.0",
            ),
        )
        log(f"[ok] MIMII toy -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "MIMII dev toy subset", out, str(exc)))
        log(f"[fail] MIMII: {exc}")


def fetch_iof(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["iof"]
    entry_id = "iof"
    repo_dir = out / "_repo"
    try:
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        result = run_cmd(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                "Release_202502",
                "--filter=blob:none",
                "--sparse",
                "https://github.com/iofoundry/ontology.git",
                str(repo_dir),
            ]
        )
        if result.returncode != 0:
            result = run_cmd(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--filter=blob:none",
                    "--sparse",
                    "https://github.com/iofoundry/ontology.git",
                    str(repo_dir),
                ]
            )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        for pattern in ("Core", "core", "CoreOntology"):
            run_cmd(["git", "sparse-checkout", "set", pattern], cwd=repo_dir)
            run_cmd(["git", "checkout"], cwd=repo_dir)
            if any(repo_dir.rglob("*.ttl")) or any(repo_dir.rglob("*.owl")):
                break
        # flatten Core files to out/
        out.mkdir(parents=True, exist_ok=True)
        for ext in ("*.ttl", "*.owl", "*.rdf"):
            for f in repo_dir.rglob(ext):
                dest = out / f.name
                if not dest.exists():
                    shutil.copy2(f, dest)
        if dir_size(out) == 0:
            shutil.copytree(repo_dir, out, dirs_exist_ok=True)
        shutil.rmtree(repo_dir, ignore_errors=True)
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "IOF Core ontology fragment",
                out,
                url="https://github.com/iofoundry/ontology",
                license="Open (IOF/OAGi)",
            ),
        )
        log(f"[ok] IOF -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "IOF Core ontology fragment", out, str(exc)))
        log(f"[fail] IOF: {exc}")


def fetch_mcdm(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["mcdm"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "mcdm"
    try:
        random.seed(42)
        schemes = [f"scheme_{i:02d}" for i in range(1, 21)]
        indicators = [
            "correctness",
            "completeness",
            "timeliness",
            "consistency",
            "explainability",
            "cost",
            "risk",
            "throughput",
            "defect_rate",
            "availability",
            "latency",
            "maintainability",
            "security",
            "traceability",
            "expert_score",
        ]
        matrix_path = out / "decision_matrix.csv"
        with matrix_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["scheme"] + indicators)
            for s in schemes:
                row = [s] + [round(random.uniform(0.3, 1.0), 4) for _ in indicators]
                writer.writerow(row)
        weights_path = out / "indicator_weights.csv"
        with weights_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["indicator", "ahp_weight", "critic_weight", "combined_weight"])
            for ind in indicators:
                ahp = random.uniform(0.02, 0.12)
                critic = random.uniform(0.02, 0.12)
                writer.writerow([ind, round(ahp, 4), round(critic, 4), round((ahp + critic) / 2, 4)])
        readme = out / "README.txt"
        readme.write_text(
            "Synthetic MCDM input for task 1.3.x (20 schemes x 15 indicators).\n"
            "Replace with project expert scores when available.\n",
            encoding="utf-8",
        )
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "Synthetic MCDM tables",
                out,
                url="local-generated",
                license="Project internal",
            ),
        )
        log(f"[ok] synthetic MCDM -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "Synthetic MCDM tables", out, str(exc)))
        log(f"[fail] MCDM: {exc}")


def fetch_mfg009(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["mfg009"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "mfg009"
    try:
        hf_snapshot("xpertsystems/mfg009-sample", out, repo_type="dataset")
        if dir_size(out) < 100:
            raise RuntimeError("empty download")
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "mfg009-sample IIoT",
                out,
                url="https://huggingface.co/datasets/xpertsystems/mfg009-sample",
                license="See HF dataset card",
            ),
        )
        log(f"[ok] mfg009 -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(
            manifest,
            fail_entry(
                entry_id,
                "mfg009-sample IIoT",
                out,
                str(exc),
                status="optional",
            ),
        )
        log(f"[optional fail] mfg009: {exc}")


def copy_rag_sample(manifest: dict[str, Any]) -> None:
    out = DATASETS / DATASET_DIRS["rag_sample"]
    out.mkdir(parents=True, exist_ok=True)
    entry_id = "rag_sample"
    src = ROOT / "projects" / "IndustrialGraphRAG" / "inputs" / "saref"
    try:
        if not src.exists():
            raise RuntimeError("IndustrialGraphRAG not cloned yet; run clone_projects.ps1 first")
        for pattern in ("*.txt", "*.ttl", "*.xlsx"):
            for f in src.glob(pattern):
                shutil.copy2(f, out / f.name)
        if dir_size(out) == 0:
            raise RuntimeError("no SAREF sample files copied")
        record_entry(
            manifest,
            ok_entry(
                entry_id,
                "SAREF RAG sample (from IndustrialGraphRAG)",
                out,
                url=str(src),
                license="See IndustrialGraphRAG repo",
            ),
        )
        log(f"[ok] RAG sample -> {out}")
    except Exception as exc:  # noqa: BLE001
        record_entry(manifest, fail_entry(entry_id, "SAREF RAG sample", out, str(exc)))
        log(f"[fail] RAG sample: {exc}")


FETCHERS: dict[str, Callable[[dict[str, Any]], None]] = {
    "secom": fetch_secom,
    "cwru": fetch_cwru,
    "cmapss": fetch_cmapss,
    "mvtec": fetch_mvtec_bottle,
    "hai": fetch_hai,
    "mimii": fetch_mimii_toy,
    "iof": fetch_iof,
    "mcdm": fetch_mcdm,
    "mfg009": fetch_mfg009,
}

# Lower priority when --max-gb is set
LOW_PRIORITY = {"mimii", "hai", "mvtec", "mfg009"}


def save_manifest(manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def print_summary(manifest: dict[str, Any]) -> None:
    log("\n=== Dataset fetch summary ===")
    ok = sum(1 for e in manifest["entries"] if e.get("status") == "ok")
    failed = sum(1 for e in manifest["entries"] if e.get("status") == "failed")
    log(f"ok={ok} failed={failed} total_bytes={total_datasets_size():,}")
    for e in manifest["entries"]:
        status = e.get("status", "?")
        size_mb = e.get("bytes", 0) / (1024 * 1024)
        log(f"  [{status}] {e.get('id')}: {size_mb:.2f} MB - {e.get('path')}")
        if status == "failed":
            log(f"         error: {e.get('error', '')[:120]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch benchmark datasets")
    parser.add_argument(
        "--only",
        type=str,
        default="",
        help="Comma-separated keys: secom,cwru,cmapss,mvtec,hai,mimii,iof,mcdm,mfg009",
    )
    parser.add_argument("--max-gb", type=float, default=20.0, help="Skip low-priority if over budget")
    parser.add_argument("--skip-rag-copy", action="store_true", help="Skip copying SAREF from projects/")
    args = parser.parse_args()

    DATASETS.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    if MANIFEST_PATH.exists():
        manifest: dict[str, Any] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {"version": 1, "updated_at": None, "entries": []}

    selected = list(FETCHERS.keys())
    if args.only.strip():
        selected = [k.strip() for k in args.only.split(",") if k.strip()]

    max_bytes = int(args.max_gb * 1024**3)

    for key in selected:
        if key not in FETCHERS:
            log(f"[skip] unknown key: {key}")
            continue
        if key in LOW_PRIORITY and total_datasets_size() > max_bytes * 0.7:
            log(f"[skip] {key}: approaching --max-gb budget")
            record_entry(
                manifest,
                fail_entry(key, key, DATASETS / DATASET_DIRS[key], "skipped due to --max-gb"),
            )
            continue
        log(f"\n--- fetching {key} ---")
        FETCHERS[key](manifest)
        save_manifest(manifest)

    if not args.skip_rag_copy:
        log("\n--- copying RAG sample ---")
        copy_rag_sample(manifest)
        save_manifest(manifest)

    print_summary(manifest)
    save_manifest(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
