"""Load the authors' Cui effect tables from a verified OSF archive."""

import hashlib
import io
import os
import urllib.request
import zipfile

import pandas as pd


def load_cui(model="GPT", effect_type="main", archive_path=None):
    """Load paired human and LLM effect estimates from the Cui archive.

    Args:
        model (str): "GPT", "Claude", or "DeepSeek".
        effect_type (str): "main" for main effects or "int" for interactions.
        archive_path (str or path-like, optional): A local copy of the selected
            model's original ZIP. If omitted, download it directly from OSF.

    Returns:
        pandas.DataFrame: The authors' enhanced effect table, without changes.

    Notes:
        Source: https://osf.io/j6wmn/. SHA256 hashes identify the files verified
        on 10 October 2026. OSF declares no data or code licence. This function
        retrieves the source archive and does not redistribute its contents.
        Workshop reading: https://arxiv.org/abs/2409.00128v3.

        Rows are effects, not paired human and simulated participants. The
        recoded LLM effect sign uses agreement with the observed human effect.
        It is therefore not a prospectively oriented prediction for PPI.
        Downloaded ZIP contents are read in memory; no archive code is run.
        Downloads are not cached. Pass archive_path to reuse a local copy.
    """
    if model not in ("GPT", "Claude", "DeepSeek"):
        raise ValueError('Choose model="GPT", "Claude", or "DeepSeek".')
    if effect_type not in ("main", "int"):
        raise ValueError('Choose effect_type="main" or "int".')
    if archive_path is not None and not isinstance(archive_path, (str, os.PathLike)):
        raise ValueError("archive_path must be a local file path or None.")

    url, expected_hash = _archive_source(model)
    if archive_path is None:
        with urllib.request.urlopen(url, timeout=60) as response:
            archive_bytes = response.read()
    else:
        with open(archive_path, "rb") as source:
            archive_bytes = source.read()

    actual_hash = hashlib.sha256(archive_bytes).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError(
            "The archive does not match the verified Cui source. "
            "Check the selected model and file, or whether OSF has changed."
        )

    member = f"{model}/enhanced_dataset_{model}_{effect_type}.csv"
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        with archive.open(member) as source:
            effects = pd.read_csv(source, encoding="utf-8-sig")
    return effects


def _archive_source(model):
    sources = {
        "GPT": (
            "https://osf.io/download/9b2jg/",
            "c0a7864c5f08cf4ee80e21eeab060582ecc30c5c100e0bbed8df36f075888eac",
        ),
        "Claude": (
            "https://osf.io/download/2w7cz/",
            "3b0d4c28efdb762d1ef5ccbabc686007ab7bd9b12f1ced4862969e5384beae2b",
        ),
        "DeepSeek": (
            "https://osf.io/download/g9fnv/",
            "6124cb2050c33cb4aa4de7666058aa2ab949d00b58c3cb1f71292e2ee7066f25",
        ),
    }
    return sources[model]
