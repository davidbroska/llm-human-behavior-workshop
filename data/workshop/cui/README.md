# Cui archive

Compare human and LLM effect estimates across scenario-based experiments in psychology and management. The workshop reading is [Cui, Li and Zhou, preprint v3](https://arxiv.org/abs/2409.00128v3), revised 20 June 2025.

The data come from the authors' [OSF archive](https://osf.io/j6wmn/). This folder includes their six final effect tables, study metadata and variable definitions for the educational workshop. Files are copied unchanged and documented in [provenance.json](provenance.json).

## Guided example · Ames and Mason’s catering experiment

Open [the Cui notebook](../../../notebooks/03_cui.ipynb). Participants imagine arranging a fundraising dinner and responding to a caterer’s opening offer. The notebook follows [Ames and Mason (2015)](https://www.columbia.edu/~da358/publications/Tandem_anchoring.pdf), Study 1, pages 257–258 and Table 1.

- Compare a $100 point offer with $100–$120, $90–$110 and $80–$100 ranges.
- Examine the assumed minimum acceptable price, counteroffer and anticipated settlement.
- Calculate each effect as range minus point offer, in dollars per person.
- Change the outcome, range or model and compare conclusions.

The prepared [catering_comparisons.csv](catering_comparisons.csv) contains nine rows per model with simpler column names. It is rebuilt with `python scripts/prepare_catering.py`; [catering_provenance.json](catering_provenance.json) records its source hashes. Means are unchanged. The original effect tables remain available.

The nine rows for `JPSP_9_1` (effect IDs 514–522) already contain the condition means for humans and each model. Group 1 is the point offer; group 2 is the named range. Human means match the rounded values in the original Table 1. The core exercise uses these means rather than the archive’s converted effect sizes or recoded signs. It does not fabricate participant records or confidence intervals.

All required tables are included. Open the notebook inside the downloaded repository. No additional participant download is needed for the catering analysis. The optional archive section compares standardized effect magnitudes descriptively, with coding and dependence limitations explained.

## Load the data

Install `pandas` if needed. Run the following Python code from this repository's root, or in a notebook with the repository available.

```python
import pandas as pd

effects = pd.read_csv("data/workshop/cui/enhanced_dataset_GPT_main.csv")
print(effects.shape)
print(effects[["study_id", "IV", "DV", "Human_r", "Gpt_r_recode"]].head())
```

No separate OSF download or model API key is needed for these tables. For another model, replace `GPT` with `Claude` or `DeepSeek`; for interactions, replace `main` with `int`.

The original-source loader remains available if you want to verify or retrieve the authors' ZIP directly. It checks the archive's SHA256 hash and reads the selected table in memory without running the authors' code. Each call downloads the ZIP unless you supply a local copy.

```python
from scripts.load_cui import load_cui

claude = load_cui(model="Claude")
interactions = load_cui(model="GPT", effect_type="int")

# Reuse a previously downloaded original ZIP, including when working offline.
effects = load_cui(model="GPT", archive_path="data/raw/GPT.zip")
```

`archive_path` must point to the original ZIP for the chosen model. The loader checks the same hash for local and downloaded files. It does not create or populate `data/raw/`.

## Understand the rows

- Each row pairs a human effect estimate with an estimate from one model. Rows are not individual human responses.
- `effect_id` identifies an effect within the main-effect or interaction table. The two tables reuse IDs, so do not join them on `effect_id` alone.
- `study_id` identifies a study. Several outcomes and contrasts may come from the same study and share participants or conditions.
- `IV` and `DV` describe the treatment or predictor and outcome. Interaction tables also include `moderator`.
- `Human_r` is the human effect converted to a common metric. The model column is `Gpt_r_recode`, `Claude_r_recode` or `DeepSeek_r_recode`.
- `human_size` records the human sample size for the effect. It is not a count of independent effects.
- Missing values remain missing. Some original fields use `/` for values that were unavailable or did not apply.

The model's recoded sign uses its agreement with the observed human effect. That is useful for reproducing the authors' comparisons, but it is not an independently oriented prediction for prospective PPI. Define a fixed treatment contrast before attempting such an analysis. A correlation across these effect estimates also does not give the participant-level PPI correlation.

`replication_success` is defined for significant human findings with codable directions. A missing value is not a failed replication. Use the original coding sheets if you want to study exclusions such as constant model outputs.

## Files and provenance

The loader reads the authors' final tables without filtering or changing their values.

| Model | Source archive | Main-effect member | Rows, main / interaction | ZIP size |
|---|---|---|---:|---:|
| GPT-4 | [GPT.zip](https://osf.io/download/9b2jg/) | `GPT/enhanced_dataset_GPT_main.csv` | 690 / 164 | 48.8 MB |
| Claude | [Claude.zip](https://osf.io/download/2w7cz/) | `Claude/enhanced_dataset_Claude_main.csv` | 683 / 164 | 34.7 MB |
| DeepSeek | [DeepSeek.zip](https://osf.io/download/g9fnv/) | `DeepSeek/enhanced_dataset_DeepSeek_main.csv` | 618 / 131 | 35.3 MB |

For interactions, the member name ends in `_int.csv`. Archive URLs and full SHA256 hashes are recorded in [the loader](../../../scripts/load_cui.py). The hashes pin the source files verified on 10 October 2026. The loader stops if the bytes change.

Additional source files

- [Authors' README](SOURCE_README.md), [variable definitions](<README for data processing procedure.xlsx>) and [study characteristics](study_info.xlsx) are included locally. The source links below allow verification and further exploration.
- [Variable definitions](https://osf.io/download/md98h/) in `README for data processing procedure.xlsx`, sheet `Explanations for Variables`.
- [Study characteristics](https://osf.io/download/qc8n6/) in `study_info.xlsx`.
- [Text prompts](https://osf.io/download/y35zx/) in `prompt.xlsx`. Select the study using `Journal`, `Essay` and `Study`; `Group` identifies the condition.
- [Simulated respondent records](https://osf.io/download/xpt2r/) in the study-level analysis ZIP. These contain model responses, not human respondent records.

Rebuild the included files with `python3 scripts/prepare_cui.py` from the repository root, using the local source collection. The preparation script verifies the original archives and copies the selected files byte for byte.

Please credit Cui, Li and Zhou and the OSF replication archive. The OSF project declares no data or code licence as of the verification date; no new dataset licence is assigned here. The preprint is separately licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
