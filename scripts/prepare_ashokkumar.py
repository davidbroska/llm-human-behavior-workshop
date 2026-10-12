"""Prepare Ashokkumar teaching data using Python and base R for RDS decoding."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile

import numpy as np
import pandas as pd


def prepare_ashokkumar(source_path, effects_path, output_dir):
    """Prepare the effect archive and a party-matched Connors candidate.

    Args:
        source_path (str): Original Code Ocean capsule export ZIP.
        effects_path (str): Published fig1_panelA.csv from the same capsule.
        output_dir (str): Destination outside the source archive.
    Returns:
        dict: Source, exclusions and matching information.
    Notes:
        R only decodes the source objects. No authors' analysis code is run.
        Predictions use model responses, weights and persona party, never Y.
        The resulting party-group predictor is a workshop construction, not
        a person-specific digital twin provided by the authors. Data are CC0.
    """
    source = Path(source_path)
    effects = Path(effects_path)
    output = Path(output_dir)
    expected_zip = "96e13b405e97700e041addb37a49f20d26d8c9d3d50d2ca8ed1b22121b7007f7"
    expected_effects = "0da13b00b57f0ac861f42c996235f0bfee48b854d05a09ba412cf2bb2d9074d8"
    for path, expected in [(source, expected_zip), (effects, expected_effects)]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Source does not match the pinned file: {path.name}")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        with zipfile.ZipFile(source) as archive:
            for name in ["rct_responses.RDS", "llm_responses.RDS"]:
                (folder / name).write_bytes(archive.read("data/" + name))
            for name in ["RA_study_features.csv", "RA_outcome_features.csv", "LICENSE"]:
                (output / name).write_bytes(archive.read("data/" + name))
        reader = folder / "read_source.R"
        reader.write_text('''
args <- commandArgs(trailingOnly = TRUE)
folder <- args[1]
h <- readRDS(file.path(folder, "rct_responses.RDS"))
i <- which(h$study == "Connors1226" & h$outcome.name == "rate_republicans")
stopifnot(length(i) == 1)
d <- h$data[[i]]
d$source_row <- seq_len(nrow(d))
write.csv(d, file.path(folder, "human.csv"), row.names = FALSE, na = "")
p <- readRDS(file.path(folder, "llm_responses.RDS"))
p <- p[p$model == "gpt-4" & p$study == "Connors1226" &
       p$outcome.name == "rate_republicans", ]
p <- p[, c("condition.name", "prompt", "expectation", "weight", "scale_flip",
           "outcome_scale_min", "outcome_scale_max")]
write.csv(p, file.path(folder, "predictions.csv"), row.names = FALSE, na = "")
''')
        subprocess.run(["Rscript", str(reader), str(folder)], check=True)
        human = pd.read_csv(folder / "human.csv")
        predicted = pd.read_csv(folder / "predictions.csv")
    predicted["pid_3"] = predicted.prompt.map(_party)
    if predicted.pid_3.isna().any():
        raise ValueError("A model persona has no recognized party affiliation.")
    predicted["Yhat"] = np.where(
        predicted.scale_flip,
        predicted.outcome_scale_max - predicted.expectation + predicted.outcome_scale_min,
        predicted.expectation,
    )
    if not ((predicted.outcome_scale_min == 0) & (predicted.outcome_scale_max == 100)).all():
        raise ValueError("Expected Republican ratings on a 0 to 100 scale.")
    predicted["weighted_prediction"] = predicted.Yhat * predicted.weight
    keys = ["condition.name", "pid_3"]
    grouped = predicted.groupby(keys)[["weighted_prediction", "weight"]].sum().reset_index()
    if (grouped.weight <= 0).any():
        raise ValueError("Persona group weights must be positive.")
    grouped["Yhat"] = grouped.weighted_prediction / grouped.weight
    selected = human[human["condition.name"].isin(["Control", "Private Reminder"])].copy()
    paired = selected.merge(grouped[keys + ["Yhat"]], on=keys,
                            how="left", validate="many_to_one")
    missing_y = int(paired.y.isna().sum())
    missing_prediction = int(paired.Yhat.isna().sum())
    paired = paired.dropna(subset=["y", "Yhat"]).copy()
    paired["treated"] = (paired["condition.name"] == "Private Reminder").astype(int)
    paired = paired.rename(columns={"y": "Y"})
    paired = paired[["source_row", "treated", "Y", "Yhat"]].sort_values("source_row")
    paired.to_csv(output / "connors_privacy.csv", index=False)
    grouped.to_csv(output / "connors_party_predictions.csv", index=False)
    (output / "effects.csv").write_bytes(effects.read_bytes())
    provenance = {
        "source_url": "https://codeocean.com/capsule/9843791/tree/v1",
        "source_doi": "10.24433/CO.6384242.v1",
        "capsule_sha256": expected_zip,
        "effects_sha256": expected_effects,
        "source_rows_in_two_arms": len(selected),
        "missing_human_outcome": missing_y,
        "missing_prediction": missing_prediction,
        "complete_rows": len(paired),
        "study": "Connors1226",
        "outcome": "rate_republicans",
        "matching": "GPT-4 weighted mean by condition and persona party, pooling template groups; joined to human condition and pid_3. Leaners mapped to their named party; other recognized affiliations to Independent.",
        "selection": "Provisional teaching example; complete cases, both partisans and independents; outcome is one component, not the original polarization measure.",
        "license": "CC0-1.0 (capsule data/LICENSE)",
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


def _party(prompt):
    for pattern in [r"partisan affiliation\?\n\n[^\n]+?: '([^']+)'",
                    r"identif(?:ies|y) as '([^']+)'"]:
        match = re.search(pattern, prompt)
        if match:
            text = match.group(1)
            if "Democrat" in text:
                return "Democrat"
            if "Republican" in text:
                return "Republican"
            if text in ("Independent", "Other", "No preference"):
                return "Independent"
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="studies/ashokkumar2026_nature/data_code/codeocean_capsule_9843791_v1_export.zip")
    parser.add_argument("--effects", default="studies/ashokkumar2026_nature/data_code/codeocean_capsule_9843791_v1/results/plot_data/fig1_panelA.csv")
    parser.add_argument("--output", default="data/workshop/ashokkumar")
    args = parser.parse_args()
    print(json.dumps(prepare_ashokkumar(args.source, args.effects, args.output), indent=2))
