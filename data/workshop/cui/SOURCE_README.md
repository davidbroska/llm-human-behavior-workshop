# LLM Data and Code: Paper Replication of Human Experiments

This repository contains data and code for a research project replicating human psychological experiments using Large Language Models (LLMs). The project systematically evaluates how GPT-4, Claude, and DeepSeek respond to the same experimental conditions as human participants across multiple psychological studies.

## Project Overview

This research investigates whether LLMs can replicate results from human psychological experiments. By presenting LLMs with identical experimental conditions used in the original studies, we compare LLM responses with human responses to assess their understanding of human psychology and potential utility as research tools.

Models used in this research:
- **GPT-4**: Default temperature of 1.0, with additional analyses at temperatures 0 and 0.5
- **Claude**: Default temperature settings
- **DeepSeek**: Temperature set to 1.3 (optimized for conversational scenarios)

## Repository Structure

The repository is organized into three main directories:

### 1. LLM API Calls (01 LLM API Calls)

Contains code and documentation for making API calls to different LLM models:

- **prompt/**: Prompts used to query the LLMs
- **script/**: Scripts for making API calls (`script_gpt.py`, `script_gpt_image.py`, `script_claude.py`, etc.) and scripts for extracting JSON-format responses (`extract_json.py`)
- **output/**: Raw output data from the LLM API calls (`{Journal}_{Essay}_{Study}_{Group}.xlsx`)
- **README_LLMs API Calls.docx**: Documentation for the API call process

Note: We applied the following standardized data processing steps to transform raw output data (`{Journal}_{Essay}_{Study}_{Group}.xlsx`) into study-level analysis data (`{Journal}_{Paper}_{Study}.xlsx`,`{Journal}_{Paper}_{Study}_c.xlsx`,`{Journal}_{Paper}_{Study}_d.xlsx`):
1. Data Cleaning: We removed rows with missing or redundant responses, and retained a number of responses consistent with the original sample size for each group, as specified in the “Group_SampleNum” column of prompt.xlsx/prompt_image.xlsx.
2. Data Merging: We merged data from all groups within each study into a single dataset. A unique "ID" column was added, with group-specific identifiers assigned sequentially (e.g., “A1–An” for Group A, “B1–Bn” for Group B, etc.).
3. Variable Coding and Aggregation: We renamed item columns (e.g., "item1", "item2", …) to reflect the actual constructs being measured, based on the original study materials. Reverse-coded items were adjusted accordingly. Finally, items were aggregated to form composite variables for analysis.

### 2. Study-level Analysis (02 Study-level analysis)

Contains `study_info.xlsx` which includes study-level variables (sample, platform, variables, citation, etc.) of the original human studies. These variables are hand-coded or drawn from the original published articles and related online sources.
Contains individual analyses for each replicated study. Each study folder follows the naming convention `[Journal]_[Paper]_[Study]`, where:
- Journal: OBHDP (Organizational Behavior and Human Decision Processes), JPSP (Journal of Personality and Social Psychology), JEP (Journal of Experimental Psychology), etc.
- Paper and Study: Specific paper and study number

Each study folder contains:
- **Data files**:
  - `{Journal}_{Paper}_{Study}.xlsx`: GPT-4 (temperature = 1.0) data
  - `{Journal}_{Paper}_{Study}_c.xlsx`: Claude data
  - `{Journal}_{Paper}_{Study}_d.xlsx`: DeepSeek data

- **Analysis scripts**:
  - R scripts (`.R`): Statistical analyses, often used for computing Cohen's d
  - SPSS scripts (`.sps`): Statistical analyses following original study methodology
  - Python scripts (`.py`): Additional analyses where applicable
  - Stata scripts (`.do`): Additional analyses where applicable

Note: Some studies use multiple analysis scripts (e.g., initial analysis in SPSS followed by Cohen's d calculation in R for consistency).

### 3. LLM Replication Analysis (03 LLM replication analysis)

Contains aggregated analyses across all studies, organized by LLM type:

- **GPT/**: Analysis of GPT-4 replications
- **Claude/**: Analysis of Claude replications
- **DeepSeek/**: Analysis of DeepSeek replications
- **Mutiple_LLM/**: Comparative analysis across LLM models

Within each LLM subdirectory, you'll find:

1. **Input Data**:
   - `original_coding_LLM_main.csv`: Coding data for main effects
   - `original_coding_LLM_int.csv`: Coding data for interaction effects

Note: For each effect, we manually reviewed and coded the relevant information from the analysis results and  `study_info.xlsx` with study_id as the unique identifier, combining them into a unified dataset for comprehensive analysis.

2. **Data Processing Pipeline**:
   - **Step 1**: Metric Conversion
     - Script: `1.metric_conversion_LLM_main.py` / `1.metric_conversion_LLM_int.py`
     - Input: `original_coding_LLM_main.csv` / `original_coding_LLM_int.csv`
     - Output: `processed_LLM_main.csv` / `processed_LLM_int.csv`
     - Purpose: Standardizes different effect size metrics (r, Fisher's Z, CI)
     - Note: Handles range-based p-values (e.g., <.001) by computing numeric values

   - **Step 2**: Main Analysis
     - Script: `2.main_analysis_LLM_main.py` / `2.main_analysis_LLM_int.py`
     - Input: `processed_LLM_main.csv` / `processed_LLM_int.csv`
     - Output: `enhanced_dataset_main.csv` / `enhanced_dataset_int.csv`
     - Purpose: Filters data and creates variables like `strict_direction`
     - Note: Excludes cases where LLMs produced identical outputs across conditions

   - **Step 3**: Visualization and Analysis
     - Scripts: Various visualization and analysis scripts
     - Input: Enhanced datasets
     - Output: Visualization files and statistical results

   - **Step 4**: Power Analysis
     - Script: `power_analysis_LLM.py`
     - Input: Enhanced datasets
     - Output: `power_analysis_results.csv`
     - Purpose: Calculates required sample sizes for replication

   - **Step 5**: Regression Analysis
     - Script: `regression.do`
     - Input: Enhanced datasets
     - Output: regression tables in the article and Supplementary Section 14
     - Purpose: Regression results of replication success, effect size difference, and direction consistency

   - **Step 6**: Decomposing Effect Size Differences
     - Script: `mean difference versus sd_LLM.R`
     - Input: Enhanced datasets
     - Output: analysis results reported in Supplementary Section 12
     - Purpose: Analyses to disentangle the relative contributions of (1) increased effect magnitude in LLM data, and (2) decreased response variation in LLM data.

3. **Results**:
   - `/results`: Statistical results (e.g., `fisher_z_ci_analysis.txt`, `replication_rates_new.csv`)
   - `/main_visual`: Generated figures and visualizations

### 4. Temperature Analysis (temperature)

A separate directory dedicated to analyzing the effects of temperature settings on GPT-4's performance in replicating human studies:

- **01 LLM API Calls/**: API calls for GPT-4 with different temperature settings
- **02 study-level analysis/**: Study-level analyses for temperature variations
- **03 LLM replication analysis/**: Aggregated analyses of temperature effects

This directory follows a similar structure to the main directories but focuses specifically on comparing GPT-4 performance across different temperature settings (0, 0.5).

## Data Processing Workflow

The complete data processing workflow follows these steps:

1. **LLM API Calls**: Generate LLM responses to experimental conditions
   - Input: Structured prompts based on original experimental materials
   - Output: LLM responses for each experimental condition
   - Code: API call scripts for each model type

2. **Study-level Analysis**: Analyze each study individually
   - Input: Clearned LLM response data for each study
   - Output: Effect sizes, p-values, and statistical results
   - Code: Study-specific analysis scripts

3. **Data Integration**: Compile study-level data into coding sheets
   - Output: `original_coding_LLM_main.csv`, `original_coding_LLM_int.csv`
   - Content: Basic info, human/LLM means, SD, effect sizes, p-values

4. **Metric Standardization**: Convert effect sizes to common formats
   - Input: Original coding sheets
   - Output: `processed_LLM_main.csv`, `processed_LLM_int.csv`
   - Code: `metric_conversion_LLM_main.py`, `metric_conversion_LLM_int.py`

5. **Data Enhancement**: Filter and prepare data for final analyses
   - Input: Processed datasets
   - Output: `enhanced_dataset_main.csv`, `enhanced_dataset_int.csv`
   - Code: `main_analysis_LLM_main.py`, `main_analysis_LLM_int.py`

6. **Statistical Analysis and Visualization**: Generate results and figures
   - Input: Enhanced datasets
   - Output: Statistical results and visualizations
   - Code: Visualization and analysis scripts

## Key Variables

The datasets contain the following key variables:

- **effect_id**: Unique identifier for each effect
- **journal, paper, study**: Source information
- **human_size**: Sample size in the original human study
- **human_direction/LLM_direction**: Effect direction (pos, neg, multi-group)
- **direction**: Whether human and LLM directions match (1=same, 0=different, /=multiplegroup)
- **human_effsize/LLM_effsize**: Effect sizes before standardization
- **human_p_value/LLM_p_value**: p-values from statistical tests
- **human_sig/LLM_sig**: Significance status (sig/nonsig at p < 0.05)
- **strict_direction**: Filtered directional variable (1, 0, or NaN)
- **Study metadata**: Sample type, platform, variable types, etc.

## Reproduction Instructions

To reproduce the analyses:

1. **Generate LLM Responses**:
   - Use scripts in "01 LLM API Calls/script/"
   - Input: Prompts from "01 LLM API Calls/prompt/"

2. **Perform Study-level Analysis**:
   - Use scripts in each study folder
   - Input: Study-specific data files (which are manually clearned from LLM responses)

3. **Run LLM Replication Analysis**:
   - Metric conversion → Main analysis → Visualization → Power analysis
   - Input: Coding sheets → Processed data → Enhanced datasets
   - Output: Final results and visualizations

Note: The `enhanced_dataset_main.csv` and `enhanced_dataset_int.csv` files are the final datasets used for analyses in the manuscript.

## Additional Information

For detailed information about specific analyses, variable definitions, and data processing steps, refer to the individual script files and README documents within each directory. 