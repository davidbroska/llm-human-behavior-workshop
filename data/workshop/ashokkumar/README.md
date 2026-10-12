# Ashokkumar archive

These files support two exercises based on [Ashokkumar et al., Large language models can predict the results of social science experiments](https://doi.org/10.1038/s41586-026-10742-x). The original data are in [Code Ocean capsule v1](https://codeocean.com/capsule/9843791/tree/v1), DOI 10.24433/CO.6384242.v1.

## Compare experimental effects

[effects.csv](effects.csv) is an unchanged copy of the published `results/plot_data/fig1_panelA.csv`. It contains 3,356 contrasts with paired observed and GPT-4 ensemble-predicted effects.

```python
import pandas as pd

effects = pd.read_csv("data/workshop/ashokkumar/effects.csv")
print(effects[["study", "estimate", "prediction"]].head())
```

- `study` identifies the experiment.
- `outcome.name` identifies the outcome.
- `reference_condition` and `condition.name` define the contrast. Effects are condition minus reference.
- `estimate` is the human effect and `prediction` is the model effect. Outcomes were rescaled to 0 to 1 before effects were computed.
- `group` is the authors' published/unpublished classification for the figure.

Use [RA_study_features.csv](RA_study_features.csv) for titles, source links and study characteristics, and [RA_outcome_features.csv](RA_outcome_features.csv) for outcome coding. Both are unchanged source files.

Several rows share participants, outcomes or reference groups; some reverse the same contrast or represent authors' hypotheses. These are not 3,356 independent experiments. This file supports descriptive comparisons, but does not provide the sampling covariance needed for a full meta-analysis. Do not average all rows as if every study contributed independent evidence equally.

## Guided example · Haaland and Roth

The [participant notebook](../../../notebooks/01_ashokkumar.ipynb) focuses on *Beliefs about Racial Discrimination and Support for Pro-Black Policies*, published in The Review of Economics and Statistics 105(1), 40–53 (2023). [Published paper](https://doi.org/10.1162/rest_a_01036) · [Open accepted manuscript](https://wrap.warwick.ac.uk/id/eprint/151133/).

The description follows the authors’ accepted manuscript, Section II. Both groups read about a correspondence study of hiring discrimination and estimate how often applications with Black-sounding names received a callback. The information treatment reveals the study’s finding of a 50 percent callback advantage for white-sounding names. The control group proceeds without receiving that result.

[haaland_responses.csv](haaland_responses.csv) contains the three archived outcomes on their original 1–5 scales.

| Outcome | Meaning | Complete responses |
|---|---|---:|
| Racial Discrimination perception | Perceived seriousness of racial discrimination in the labor market | 1,534 |
| Affirmative action: Preference | Support for preference for qualified Black applicants over equally qualified white applicants | 1,532 |
| Affirmative action: Assistance | Support for employment assistance to qualified Black applicants | 1,529 |

Larger values indicate greater perceived seriousness or support. Each outcome starts with 1,542 source rows. Missing human responses number 4, 7 and 9 respectively; five rows per outcome lack a party-group prediction. These exclusions overlap. Inference concerns complete cases.

Columns are `outcome`, `source_row`, `treated` (1 information, 0 control), `Y` and `Yhat`. The row identifier is specific to each outcome table. It must not be used to join different outcomes as if it were a verified person identifier.

Predictions are weighted GPT-4 means within outcome, condition and persona party, pooling available prompt templates. Human respondents receive their party’s prediction in their assigned condition. Leaners are assigned to their named party. No human outcome is used in constructing predictions. These are group predictions, not digital twins or the original paper’s ensemble-effect estimates. [haaland_party_predictions.csv](haaland_party_predictions.csv) records the group means.

The original study measures additional beliefs and behavior. The stored perceived-seriousness item is not its quantitative belief-updating measure or a verified manipulation check. Comparing effects across the three available outcomes does not identify causal mediation. The notebook retains the individual outcome definitions and uses simple unadjusted comparisons, rather than reproducing every original specification.

Rebuild this extract with `python scripts/prepare_haaland.py` from the repository root. The script verifies the source capsule hash and uses base R only to decode the data. [haaland_provenance.json](haaland_provenance.json) records the source, exclusions and construction. Cite Haaland and Roth and Ashokkumar et al.

## Archive-wide PPI exploration

The notebook explores treatment-coefficient PPI correlations and approximate effective sample size gains for a fixed half-labeled/half-unlabeled design. No costs or budget are needed.

- [archive_responses.csv.gz](archive_responses.csv.gz) contains 212,581 complete outcome rows across 69 study IDs. Rows are not necessarily unique people across outcomes. Columns are `study`, `outcome`, `source_row`, `condition`, `Y` and `Yhat`, on the original scales.
- [archive_ppi.csv](archive_ppi.csv) contains 1,675 unordered condition pairs, all evaluable for the fixed-size calculation. Any numerical failures from future preparations are retained in `status`. `reference` and `comparison` are in lexical order, not necessarily the study’s designated control and treatment.
- [archive_ppi_coverage.csv](archive_ppi_coverage.csv) includes all 71 source study IDs. `bucci1408` lacks the party field needed for matching; `willer845` has no matching GPT-4 predictions. These are not assigned zero correlation.

The extract uses the same pinned Code Ocean capsule and party matching as the Haaland preparation. Predictions are weighted within study, outcome, condition and party. Human outcomes are never used to construct them. Source hashes remain in `haaland_provenance.json` and the source verification in the scripts.

Rebuild with `python scripts/prepare_archive_ppi.py`. The script requires the notebook’s pinned `ppi_py` version. It includes all unordered pairs with at least ten complete people per condition and variable human outcomes. All complete responses are pilot data for the correlation. Check each original design before interpreting a pair causally; pairs share people and are not independent experiments.

`labeled_n` and `unlabeled_N` split each pair’s complete people approximately in half. `effective_n` is the idealized equivalent number of human observations, calculated as `n / (1 - rho**2 * N/(n+N))`. `ess_gain_percent` compares that with `n`. This is a large-sample optimal-weighting approximation, not the realized precision of an interval. For negative correlations the implied gain requires reversing the predictor or allowing negative tuning weights.

The helper uses the same package routines that `ppi_ols_power` uses to compute its parameter-specific correlation, without invoking the allocation optimizer. The package version is pinned. The fixed-size ESS calculation uses no costs. The guided example estimates correlation from its labeled half, whereas the archive uses all complete cases as pilot data.

## Optional alternative · Connors

[connors_privacy.csv](connors_privacy.csv) uses one contrast from [Connors (2023), Social Desirability and Affective Polarization, Study 4](https://doi.org/10.1093/poq/nfad053).

- People are either reminded that their answers are private or receive no reminder.
- The outcome is their rating of Republicans on a 0 to 100 feeling thermometer.
- We ask whether model predictions can help estimate the effect of the reminder using fewer observed answers.

| Column | Meaning |
|---|---|
| `source_row` | Row number within the original study-outcome human table, before exclusions |
| `treated` | 1 for Private Reminder, 0 for Control |
| `Y` | Observed Republican rating, 0 to 100 |
| `Yhat` | GPT-4 prediction for the person's party group in that condition, 0 to 100 |

```python
data = pd.read_csv("data/workshop/ashokkumar/connors_privacy.csv")
Y = data["Y"].to_numpy()
Yhat = data["Yhat"].to_numpy()
treated = data["treated"].to_numpy()
```

### How predictions were assigned

The source contains individual human responses and separate model simulations of personas. It does not directly provide a twin for each human respondent.

The preparation script selects GPT-4 responses for `Connors1226`, outcome `rate_republicans`. It reads party affiliation from each persona's prompt, maps leaners to the named party, and averages model responses within party and condition using the supplied weights. It then assigns that group prediction to human respondents with the corresponding `pid_3` and condition. No observed human rating is used to construct the predictions. [connors_party_predictions.csv](connors_party_predictions.csv) records the group means and weight totals.

This is a workshop predictor based on party, not the authors' original ensemble-effect analysis or an exact match on six demographics. Different people in the same party and condition receive the same prediction. Its usefulness may largely reflect differences in ratings between parties.

The source contains 1,633 people in the two conditions. We exclude 68 missing human ratings, leaving 1,565 complete cases, with 773 controls and 792 treated respondents. Every selected row has a group prediction. Inference from this extract concerns the complete-case population; the exercise does not establish that missing outcomes are ignorable for the full recruited population.

The original article studies affective polarization among partisans. This teaching extract includes independents and uses Republican ratings alone, not the in-party minus out-party polarization measure. It should not be described as a direct replication of the paper's main analysis. It uses the published privacy treatment.

## Reproduce

[prepare_ashokkumar.py](../../../scripts/prepare_ashokkumar.py) verifies both source hashes and rebuilds these files. It needs Python with NumPy and pandas, and base R to read the RDS objects. Participants only need the prepared CSVs. The script does not execute code from the capsule.

From the repository root, using the local source collection:

```bash
python3 scripts/prepare_ashokkumar.py
```

Use `--source`, `--effects` and `--output` for other file locations. Reading the full LLM RDS temporarily uses substantially more memory than the final extract. The 468 MB processed-results cache is unnecessary.

[provenance.json](provenance.json) records source hashes, exclusions and the matching rule. The capsule's [CC0 licence](LICENSE) covers its data. Please cite Ashokkumar et al. (2026) and Connors (2023) when using the response example.
