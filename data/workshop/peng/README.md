# Peng archive

Compare what people said with what their digital twins predicted. These files use the default GPT-4.1 specification, with full personas, no reasoning, and temperature 0.7. They contain existing predictions; no model calls are needed.

Source reading is [Peng et al., Digital twins are funhouse mirrors](https://doi.org/10.1126/sciadv.aeh8260). Study descriptions below follow Supplementary Information sections S10.2, S10.5 and S10.7. The [Peng notebook](../../../notebooks/02_peng.ipynb) uses the gratitude experiment as a worked example. It follows the same sequence as Ashokkumar: study design, outcome comparisons, a half-human illustration, PPI correlation, effective sample size, and extensions.

## Prepared exercises

| File | Question | Observations |
|---|---|---:|
| [green_energy.csv](green_energy.csv) | Does making green energy the default change the option people choose? | 600 people |
| [gratitude_outcomes.csv](gratitude_outcomes.csv) | Does the prime change gratitude itself and the downstream composite? | 508 people, two outcomes each |
| [affective_gratitude.csv](affective_gratitude.csv) | The original workshop extract containing only the downstream composite | 508 people |
| [junk_fees.csv](junk_fees.csv) | Do twins predict knowledge of fees, perceived fairness, and support for regulation equally well? | 400 people, three outcomes each |

### Green energy

- Participants imagine choosing an energy supplier. The default is either the cheaper conventional option or the green option.
- `treated = 1` means green energy is the default, with an option to opt out. `treated = 0` means participants must opt in to green energy.
- `Y = 1` means the person chose green energy. `Yhat = 1` means their twin did. Both are binary choices, not estimated probabilities.
- There are 300 people in each arm. These are survey choices, not observed changes to electricity contracts.

### Gratitude

- Participants write about a time they felt grateful for someone's help, or about their morning routine.
- `treated = 1` is the gratitude prompt. `treated = 0` is the routine prompt.
- The outcome is the authors' downstream composite on a 1 to 7 scale. It averages an elevation scale and an empathic-concern scale about people affected by tariffs.
- This is not the immediate gratitude manipulation check. The archive's outcome name `gratitude` can otherwise be misleading.
- The file includes 251 people in the gratitude-prompt arm and 257 in the routine arm. The separate lack-of-control experiment is excluded.

This experiment is published as the Affective Primes substudy of Peng et al. Read section S10.2 of the paper's Supplementary Materials for the full design and analyses. The authors analyze the immediate gratitude manipulation check, the downstream composite, and elevation and empathic concern separately. The notebook uses `gratitude_outcomes.csv`, containing the scored manipulation check and downstream composite. It retains the original composite rather than separating its components. The older `affective_gratitude.csv` remains available and contains only the composite.

The manipulation check averages ratings of feeling grateful, thankful and appreciative. Elevation averages six items about uplifting feelings, including optimism about humanity. Empathic concern averages two items about people affected by tariffs. All use 1 to 7 response scales; the downstream composite gives equal weight to the elevation and empathic-concern scales.

For further exploration, one question is whether the composite hides different effects. The authors report an increase in elevation among humans, but essentially no change in their empathic concern. The gratitude manipulation itself is adapted from earlier research, including [Oguni and Ishii (2024)](https://doi.org/10.1038/s41598-024-65460-z). The empathy measure draws on [Oliveira et al. (2021)](https://doi.org/10.3389/fpsyg.2021.588691), adapted from COVID-19 to tariffs. Those are background studies, not the source of these human/twin observations.

### Junk fees

- Participants answer questions about fees in several industries, judge how fair the fees are, and report support for regulation.
- `percent_correct` measures knowledge on a 0 to 100 scale.
- `fairness_average` and `reg_support` are the authors' composites on 1 to 7 scales. Higher values mean greater perceived fairness and stronger support for regulation.
- Compare one outcome at a time. The three rows for each person are repeated measurements, not three independent people.
- There is no single treatment indicator in this extract. It is suited to comparing means and prediction errors, or to mean PPI, rather than the treatment-effect demo.

## Load a candidate

Run from the repository root after installing `pandas`.

```python
import pandas as pd

data = pd.read_csv("data/workshop/peng/green_energy.csv")
Y = data["Y"].to_numpy()
Yhat = data["Yhat"].to_numpy()
treated = data["treated"].to_numpy()
```

`TWIN_ID` is the authors' anonymized participant key. `variable_name` identifies the outcome. `Y` is the observed response and `Yhat` is the corresponding twin response. Joins use these keys, never row position. The same person can appear in several studies. For the PPI illustration, pretend human responses have been collected for a randomly selected half of the people in each condition. Use only predictions for the remainder; there is no separate held-out validation exercise.

## Compare the prepared experiments

[experimental_outcomes.csv](experimental_outcomes.csv) combines the two gratitude outcomes and the green-energy choice, with `study`, `outcome`, `TWIN_ID`, `variable_name`, `treated`, `Y` and `Yhat`. It contains 1,616 person-outcome rows, not 1,616 distinct participants. The notebook computes treatment-specific PPI correlations and approximate effective sample sizes for these three comparisons. It uses all responses as pilot data for this descriptive comparison and a fixed half-human design, without costs.

The new gratitude file uses the authors’ scored human and twin tables from `results/affective_priming/full_persona_without_reasoning_2025-06-18/`, specifically `Affective Primes full_persona_without_reasoning_2025-06-18 human data processed.csv` and the corresponding `twins data processed.csv`. It joins by `TWIN_ID`, verifies matching domain and condition, selects the gratitude domain, and preserves the authors’ two scores unchanged. Both outcomes have 508 complete human/twin pairs. The manipulation-check and composite scores were also checked against their component-item calculations.

## Explore all 19 studies

[default_outcomes.zip](default_outcomes.zip) contains the authors' two analysis tables for every study under the default specification. File contents are unchanged. Original paths and run dates are preserved, including the misspelling `without_resoning` in the redistribution-preferences study.

```python
import zipfile
import pandas as pd

with zipfile.ZipFile("data/workshop/peng/default_outcomes.zip") as archive:
    path = "results/default_eric/full_persona_without_reasoning_2025-06-18/"
    outcomes = pd.read_csv(archive.open(path + "meta analysis individual level.csv"))
    summary = pd.read_csv(archive.open(path + "meta analysis.csv"))
```

The individual table is long, with a human and a twin row for each participant and outcome. Pivot on `TWIN_ID` and `variable_name`, using `respondent_type` for columns and `value` for values. Study and specification must also be part of the key if you combine files.

Some outcomes are categorical. Numeric category codes are not automatically suitable for correlation. Check the outcome definition before choosing a metric. The compact archive omits treatment assignments for studies other than the two prepared treatment examples. Use the full source and study materials for additional causal comparisons.

## Reproduce or extend

[prepare_peng.py](../../../scripts/prepare_peng.py) verifies the original ZIP, selects the 38 default tables, joins paired outcomes, and adds treatment assignments from the same specification's human file. No rows with missing paired outcomes are silently removed. It stops on ambiguous assignments or duplicate keys.

From the repository root, with the original archive already downloaded:

```bash
python3 scripts/prepare_peng.py data/raw/peng_results.zip
```

To obtain all model and prompt variants from the authors:

```bash
mkdir -p data/raw
curl --fail --location 'https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500-Mega-Study/resolve/0401b715a341ac4b5f98b4424b4aecf9d29570d0/results.zip' --output data/raw/peng_results.zip
```

This is a 213.6 MB download. The pinned commit, hash, selected paths and row counts are in [provenance.json](provenance.json). The preparation script verifies the hash before reading data. The much larger base-persona dataset is unnecessary for these comparisons.

The source dataset is released under [Apache 2.0](LICENSE). The [upstream dataset card](SOURCE_README.md) is preserved. The prepared CSVs are workshop transformations, documented above; the 38 files inside the compact ZIP are unmodified. Please cite Peng et al. (2026), DOI 10.1126/sciadv.aeh8260, and credit the Twin-2K-500-Mega-Study authors.
