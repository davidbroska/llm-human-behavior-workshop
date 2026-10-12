"""Prepare teaching candidates from the pinned Peng source ZIP, without running it."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import pandas as pd


def prepare_peng(source_path, output_dir):
    """Extract default-specification outcomes and three candidate exercises.

    Args:
        source_path (str): Path to the authors' original results.zip.
        output_dir (str): Destination outside the source archive.
    Returns:
        dict: Counts for the prepared candidate files.
    Notes:
        Human and twin outcomes are joined by TWIN_ID and variable_name.
        Treatment assignment comes from the same specification's human file.
        Source DOI: 10.1126/sciadv.aeh8260. Dataset licence: Apache-2.0.
    """
    source = Path(source_path)
    output = Path(output_dir)
    expected = "548f9b2c4886515f670a0d98c1b32f90722278b976af9f31a231bf2e9dd6e2ed"
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError("The Peng source ZIP does not match the pinned version.")
    output.mkdir(parents=True, exist_ok=True)
    counts = {}
    with zipfile.ZipFile(source) as archive:
        members = sorted(n for n in archive.namelist()
                         if n.startswith("results/")
                         and "/full_persona_without_re" in n
                         and n.endswith("/meta analysis individual level.csv"))
        if len(members) != 19:
            raise ValueError("Expected one default outcome table for each of 19 studies.")
        with zipfile.ZipFile(output / "default_outcomes.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
            for member in members:
                for name in [member, member.replace(" individual level", "")]:
                    info = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    bundle.writestr(info, archive.read(name))
        for study, filename in [("default_eric", "green_energy.csv"),
                                ("affective_priming", "affective_gratitude.csv"),
                                ("junk_fees", "junk_fees.csv")]:
            member = next(n for n in members if n.split("/")[1] == study)
            data = pd.read_csv(archive.open(member))
            keys = ["TWIN_ID", "variable_name", "respondent_type"]
            if data.duplicated(keys).any():
                raise ValueError(f"Duplicate participant/outcome/type key in {study}.")
            paired = data.pivot(index=["TWIN_ID", "variable_name"],
                                columns="respondent_type", values="value").reset_index()
            paired = paired.rename(columns={"human": "Y", "twin": "Yhat"})
            if study != "junk_fees":
                raw_name = member.replace("meta analysis individual level.csv",
                                          "consolidated_original_answers_values.csv")
                raw = pd.read_csv(archive.open(raw_name), skiprows=[1, 2])
                if raw.TWIN_ID.duplicated().any():
                    raise ValueError("Treatment table has repeated participant IDs.")
                if study == "default_eric":
                    assigned = raw[["OPTIN_Green", "OPTOUT_Green"]].notna().sum(axis=1)
                    if not (assigned == 1).all():
                        raise ValueError("Each participant must have exactly one green-energy condition.")
                    raw["treated"] = raw.OPTOUT_Green.notna().astype(int)
                    paired = paired[paired.variable_name == "target_behavior_green"]
                else:
                    raw = raw[raw.emotion == "gratitude"].copy()
                    if not raw.cond.isin(["control", "prime"]).all():
                        raise ValueError("Unknown gratitude treatment condition.")
                    raw["treated"] = (raw.cond == "prime").astype(int)
                    paired = paired[paired.variable_name == "gratitude"]
                paired = paired.merge(raw[["TWIN_ID", "treated"]], on="TWIN_ID",
                                      how="left", validate="many_to_one")
                if paired.treated.isna().any():
                    raise ValueError("An outcome has no matching treatment assignment.")
            if paired[["Y", "Yhat"]].isna().any().any():
                raise ValueError("A candidate outcome is missing a human or twin response.")
            paired = paired.sort_values(["TWIN_ID", "variable_name"])
            paired.to_csv(output / filename, index=False)
            counts[filename] = len(paired)
        gratitude = _prepare_gratitude(archive, members)
        gratitude.to_csv(output / "gratitude_outcomes.csv", index=False)
        counts["gratitude_outcomes.csv"] = len(gratitude)
        green = pd.read_csv(output / "green_energy.csv")
        green["study"] = "default_eric"
        green["outcome"] = "Green-energy choice"
        experiments = pd.concat([gratitude, green], ignore_index=True)
        experiments.to_csv(output / "experimental_outcomes.csv", index=False)
        counts["experimental_outcomes.csv"] = len(experiments)
    provenance = {
        "source_url": "https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500-Mega-Study/resolve/0401b715a341ac4b5f98b4424b4aecf9d29570d0/results.zip",
        "source_sha256": expected,
        "default_outcome_members": members,
        "candidate_rows": counts,
        "selection": "Provisional teaching candidates chosen for interpretable outcomes; not a representative sample of predictive accuracy.",
        "license": "Apache-2.0 (upstream dataset card)",
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return counts


def _prepare_gratitude(archive, members):
    """Pair the original scored manipulation check and composite by TWIN_ID."""
    member = next(n for n in members if n.split("/")[1] == "affective_priming")
    folder = member.rsplit("/", 1)[0] + "/"
    prefix = "Affective Primes full_persona_without_reasoning_2025-06-18 "
    human = pd.read_csv(archive.open(folder + prefix + "human data processed.csv"))
    twin = pd.read_csv(archive.open(folder + prefix + "twins data processed.csv"))
    variables = ["gratitude_manipulation_check", "gratitude"]
    paired = human[["TWIN_ID", "emotion", "cond"] + variables].merge(
        twin[["TWIN_ID", "emotion", "cond"] + variables], on="TWIN_ID",
        suffixes=("_human", "_twin"), validate="one_to_one")
    if len(paired) != len(human) or len(paired) != len(twin):
        raise ValueError("Not every human has exactly one twin.")
    if not ((paired.emotion_human == paired.emotion_twin) &
            (paired.cond_human == paired.cond_twin)).all():
        raise ValueError("Human and twin experimental assignments differ.")
    paired = paired[paired.emotion_human == "gratitude"].copy()
    if not paired.cond_human.isin(["prime", "control"]).all():
        raise ValueError("Unrecognized gratitude condition.")
    names = {"gratitude_manipulation_check": "Gratitude manipulation check",
             "gratitude": "Downstream composite"}
    tables = []
    for variable in variables:
        d = paired[["TWIN_ID", variable + "_human", variable + "_twin"]].copy()
        d.columns = ["TWIN_ID", "Y", "Yhat"]
        d["treated"] = (paired.cond_human == "prime").astype(int)
        d["variable_name"] = variable
        d["outcome"] = names[variable]
        d["study"] = "affective_priming"
        if d[["Y", "Yhat"]].isna().any().any():
            raise ValueError("Missing scored gratitude outcome.")
        if not d[["Y", "Yhat"]].ge(1).all().all() or not d[["Y", "Yhat"]].le(7).all().all():
            raise ValueError("A gratitude score is outside 1–7.")
        tables.append(d)
    return pd.concat(tables, ignore_index=True).sort_values(["TWIN_ID", "outcome"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default="studies/peng2026_sciadv/data/hf_Twin-2K-500-Mega-Study/results.zip")
    parser.add_argument("--output", default="data/workshop/peng")
    args = parser.parse_args()
    print(prepare_peng(args.source, args.output))
