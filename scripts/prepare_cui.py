"""Copy the six Cui effect tables unchanged from checksum-verified source ZIPs."""

import hashlib
import json
from pathlib import Path
import zipfile

from load_cui import load_cui


def prepare_cui():
    """Prepare attributed local tables for the educational workshop.

    Returns:
        list: Source members, checksums and row counts.
    Notes:
        The organizer authorized including these replication tables.
        OSF declares no dataset licence; no new licence is assigned here.
        Source tables retain their original values, columns and exclusions.
    """
    root = Path(__file__).resolve().parents[1]
    source = root / "studies/cui2025_natcompsci/data_code/osf_j6wmn"
    output = root / "data/workshop/cui"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    urls = {"GPT": "https://osf.io/download/9b2jg/",
            "Claude": "https://osf.io/download/2w7cz/",
            "DeepSeek": "https://osf.io/download/g9fnv/"}
    for model in ["GPT", "Claude", "DeepSeek"]:
        path = source / "03 LLM replication analysis" / f"{model}.zip"
        for effect_type in ["main", "int"]:
            data = load_cui(model, effect_type, path)
            filename = f"enhanced_dataset_{model}_{effect_type}.csv"
            member = f"{model}/{filename}"
            with zipfile.ZipFile(path) as archive:
                content = archive.read(member)
            (output / filename).write_bytes(content)
            records.append({"file": filename, "member": member, "source_url": urls[model],
                            "rows": len(data), "sha256": hashlib.sha256(content).hexdigest()})
    for relative in ["README.md", "README for data processing procedure.xlsx",
                     "02 Study-level analysis/study_info.xlsx"]:
        path = source / relative
        name = "SOURCE_README.md" if path.name == "README.md" else path.name
        content = path.read_bytes()
        (output / name).write_bytes(content)
        records.append({"file": name, "source_path": relative,
                        "sha256": hashlib.sha256(content).hexdigest()})
    provenance = {"source": "https://osf.io/j6wmn/", "reading": "https://arxiv.org/abs/2409.00128v3",
                  "changes": "Selected files copied byte-for-byte; no transformations.",
                  "license": "No dataset licence declared in the OSF record checked 10 October 2026.",
                  "files": records}
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return records


if __name__ == "__main__":
    for record in prepare_cui():
        print(record["file"], record.get("rows", "metadata"))
