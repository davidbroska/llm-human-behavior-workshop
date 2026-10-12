---
license: apache-2.0
task_categories:
- text-generation
- question-answering
tags:
- digital-twin
- survey
- llm-simulation
- psychology
- behavioral-research
---

# Twin-2K-500-Mega-Study Dataset

**GitHub Repository**: [https://github.com/TianyiPeng/Twin-2K-500-Mega-Study](https://github.com/TianyiPeng/Twin-2K-500-Mega-Study)

To see more details for how to process these data, please refer to this GitHub repository.

This dataset contains survey data from the Twin-2K-500 Mega Study, which tests the validity of using large language models to predict people's future answers based on their answers to past surveys (creating "digital twins" of participants).

## Dataset Structure

The dataset is organized into **splits**, where each split corresponds to a different study. Each split contains a dataframe with the following structure:

- **Rows**: PID (Participant ID) - matches the Twin-2K-500 dataset
- **Columns**:
  - `PID`: Participant identifier
  - `survey_json_with_human_response`: JSON format of the survey tailored for the person (each person may see different set of questions due to randomization), with the human's answers included
  - `survey_text`: The questions text fed into LLM for simulation for this particular person (ID matches the Twin-2K-500 dataset) and specific study

## Studies Included

The dataset includes 19 studies:
- accuracy_nudges (1,003 examples)
- affective_priming (1,000 examples)
- consumer_minimalism (200 examples)
- context_effects (501 examples)
- default_eric (600 examples)
- digital_certification (600 examples)
- hiring_algorithms (999 examples)
- idea_evaluation (1,174 examples)
- idea_generation (200 examples)
- infotainment (300 examples)
- junk_fees (400 examples)
- obedient_twins (1,001 examples)
- preference_redistribution (1,198 examples)
- privacy (1,200 examples)
- promiscuous_donors (799 examples)
- quantitative_intuition (1,435 examples)
- recommendation_algorithms (598 examples)
- story_beliefs (251 examples)
- targeting_fairness (357 examples)

**Total: 13,299 examples across 19 studies**

## Additional Files

### Raw Dataset (.dat folder)

The raw dataset is in the `.dat` folder, including:
- Human's raw response CSV files
- Qualtrics QSF files (survey templates)

### Results Dataset (results.zip)

The results dataset is provided as `results.zip` and contains response CSV files for each study and specification, including:
- Response CSV from both human and LLM
- Consolidated answers in various formats (values, labels, etc.)
- Organized by study name and specification (e.g., `results/accuracy_nudges/full_persona_without_reasoning_2025-06-18/`)

## Usage

### Loading the Dataset

```python
from datasets import load_dataset

# Load the entire dataset
dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500-Mega-Study")

# Access a specific study split
accuracy_nudges = dataset["accuracy_nudges"]

# Access a specific example
example = accuracy_nudges[0]
print(example["PID"])
print(example["survey_text"])
print(example["survey_json_with_human_response"])
```

### Accessing Raw Data

The raw data files are available in the `.dat` folder:
- Raw response CSV files: `.dat/{study_name}/raw_data/response.csv`
- Qualtrics QSF files: `.dat/{study_name}/raw_data/survey.qsf`

### Accessing Results

The results files are available in the `results.zip` file:
- After extracting, human responses can be found at: `results/{study_name}/{specification}/consolidated_original_answers_values.csv`
- After extracting, LLM responses can be found at: `results/{study_name}/{specification}/consolidated_llm_values.csv`

## Citation

If you use this dataset, please cite:

```bibtex
@misc{peng2026digitaltwinsfunhousemirrors,
      title={Digital Twins as Funhouse Mirrors: Five Key Distortions}, 
      author={Tianyi Peng and George Gui and Melanie Brucks and Daniel J. Merlau and Grace Jiarui Fan and Malek Ben Sliman and Eric J. Johnson and Abdullah Althenayyan and Silvia Bellezza and Dante Donati and Hortense Fong and Elizabeth Friedman and Ariana Guevara and Mohamed Hussein and Kinshuk Jerath and Bruce Kogut and Akshit Kumar and Kristen Lane and Hannah Li and Vicki Morwitz and Oded Netzer and Patryk Perkowski and Olivier Toubia},
      year={2026},
      eprint={2509.19088},
      archivePrefix={arXiv},
      primaryClass={cs.CY},
      url={https://arxiv.org/abs/2509.19088}, 
}
```

## License

This dataset is licensed under Apache 2.0.
