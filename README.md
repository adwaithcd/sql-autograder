# SQL Autograder

An LLM-based SQL grading system using Google Gemini API to automatically grade student SQL submissions and compare with human grader scores.

## Features

- **Automated Grading**: Uses Google Gemini API to grade SQL submissions based on detailed rubrics
- **Comprehensive Analysis**: Compares LLM grading with human grader scores
- **Detailed Feedback**: Provides specific feedback and identifies submissions needing manual review
- **Per-Grader Statistics**: Analyzes grading patterns for each human grader (G1-G6)
- **Visualizations**: Generates distribution plots comparing LLM and human grading
- **Modular Design**: Clean, maintainable code structure with separate modules
- **Easy Configuration**: Simple setup via environment variables

## Project Structure
```
.
├── sql_autograder/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management
│   ├── prompts.py          # Grading prompts and rubrics
│   ├── grader.py           # LLM grading logic (Gemini API)
│   ├── data_loader.py      # CSV data loading and validation
│   ├── results.py          # Results processing and storage
│   ├── statistics.py       # Statistics generation
│   └── visualizations.py   # Visualization plots
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([get one here](https://aistudio.google.com/api-keys))

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key:

**Linux/Mac:**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY='your-api-key-here'
```

## Usage

### Complete Workflow
```bash
# 1. Set API key (once per terminal session)
export GEMINI_API_KEY='your-api-key-here'

# 2. Grade submissions (creates output/grading_results.csv)
python main.py grade exam1-submission.csv

# 3. Generate overall statistics (creates output/statistics_report.txt)
python main.py stats output/grading_results.csv

# 4. Generate per-grader statistics (creates output/per_grader_statistics.txt)
python main.py grader-stats output/grading_results.csv

# 5. Generate visualizations (creates PNG files in output/)
python main.py visualize output/grading_results.csv
```

### 1. Grading Student Submissions

**Basic usage (with default output):**
```bash
python main.py grade exam1-submission.csv
```
Creates: `output/grading_results.csv`

**With options:**
```bash
# Custom output filename
python main.py grade exam1-submission.csv --output my_results.csv

# Grade only first 50 students (for testing)
python main.py grade exam1-submission.csv --max-students 50

# Adjust rate limiting (delay between API calls in seconds)
python main.py grade exam1-submission.csv --rate-limit 2.0

# Combine options
python main.py grade exam1-submission.csv --max-students 100 --rate-limit 1.5
```

### 2. Generating Overall Statistics

**Basic usage:**
```bash
python main.py stats output/grading_results.csv
```
Creates: `output/statistics_report.txt`

**With custom output:**
```bash
python main.py stats output/grading_results.csv --output my_stats.txt
```

**Output includes:**
- Summary statistics (total students, averages, standard deviations)
- Overall agreement rate between LLM and human graders
- Per-question statistics and agreement rates
- Detailed breakdown for each of the 5 SQL questions

### 3. Generating Per-Grader Statistics

**Basic usage:**
```bash
python main.py grader-stats output/grading_results.csv
```
Creates: `output/per_grader_statistics.txt`

**With custom output:**
```bash
python main.py grader-stats output/grading_results.csv --output grader_analysis.txt
```

**Grader assignments:**
- G1: Students 1-55
- G2: Students 56-110
- G3: Students 111-165
- G4: Students 166-220
- G5: Students 221-275
- G6: Students 276-330

**Output includes:**
- Total scores comparison for each grader
- Per-question breakdown for each grader
- Agreement rates by grader and question
- Mean and standard deviation comparisons

### 4. Generating Visualizations

**Basic usage:**
```bash
python main.py visualize output/grading_results.csv
```

**With custom output directory:**
```bash
python main.py visualize output/grading_results.csv --output-dir plots/
```

**Generated files:**
- `overall_distribution.png` - Side-by-side comparison of Human vs LLM grade distribution
- `G1_distribution.png` through `G6_distribution.png` - Individual grader comparisons
- `all_graders_grid.png` - Grid view of all 6 graders

Each visualization shows:
- Human grader distribution on the left
- LLM grader distribution on the right
- Count labels on each bar
- Statistics (N, mean, standard deviation, difference)

## Input CSV Format

The input CSV file must contain these columns:

- `Student ID`: Unique student identifier
- `Name`: Student name
- `Question 4.1 Response`: SQL query for question 4.1
- `Question 4.1 Score`: Human grader score for question 4.1
- `Question 4.2 Response`: SQL query for question 4.2
- `Question 4.2 Score`: Human grader score for question 4.2
- `Question 4.3 Response`: SQL query for question 4.3
- `Question 4.3 Score`: Human grader score for question 4.3
- `Question 4.4 Response`: SQL query for question 4.4
- `Question 4.4 Score`: Human grader score for question 4.4
- `Question 4.5 Response`: SQL query for question 4.5
- `Question 4.5 Score`: Human grader score for question 4.5

**Note**: If your CSV has different column names, update them in `sql_autograder/config.py` in the `get_grading_config()` function.

## Output Files

### 1. Grading Results CSV (`output/grading_results.csv`)

Contains detailed grading information for each student:
- Student ID and name
- SQL queries submitted for each question
- Human grader scores (0-10 per question)
- LLM scores (0-10 per question)
- Score differences (LLM - Human)
- Feedback for each question
- Flags indicating if manual review is needed
- Total scores (out of 50 points)

### 2. Statistics Report (`output/statistics_report.txt`)

Overall statistics including:
- Summary statistics across all students
- Question-level agreement rates
- Per-question detailed analysis
- Average scores and standard deviations

### 3. Per-Grader Statistics (`output/per_grader_statistics.txt`)

Grader-specific analysis including:
- Total scores by grader
- Per-question breakdown for each grader
- Agreement rates for each grader
- Comparison of grading patterns

### 4. Visualizations (`output/*.png`)

- **overall_distribution.png**: Overall comparison of all students
- **G1-G6_distribution.png**: Individual grader comparisons
- **all_graders_grid.png**: Grid view of all graders

## Customizing for Your Questions

### Changing Question Numbers or Column Names

Edit `sql_autograder/config.py`:
```python
def get_grading_config() -> GradingConfig:
    # Change question numbers here
    questions = ['4.1', '4.2', '4.3', '4.4', '4.5']
    
    # Change CSV column names here to match your file
    question_columns = {
        '4.1': {'response': 'Question 4.1 Response', 'score': 'Question 4.1 Score'},
        # ... update as needed
    }
```

### Customizing Rubrics

Edit `sql_autograder/prompts.py`:

1. Update the database schema in the prompt
2. Modify question descriptions
3. Change correct answers
4. Adjust deduction rules

The prompt is well-structured and clearly commented for easy modification.

## Understanding the Results

### Agreement Rate
The percentage of submissions where LLM and human graders gave the same score (within 0.1 points).

**Interpretation:**
- **High agreement (>80%)**: Strong alignment between LLM and human grading
- **Moderate agreement (60-80%)**: Reasonable alignment, some manual review recommended
- **Low agreement (<60%)**: Significant differences, careful review needed

### Score Difference
- **Positive values** (e.g., +0.5): LLM scored higher than human grader (more lenient)
- **Negative values** (e.g., -0.5): LLM scored lower than human grader (more strict)
- **Near zero** (e.g., -0.1): Strong agreement between LLM and human

### Needs Review Flag
Submissions automatically flagged for manual review when:
- Query is ambiguous or unclear
- Edge cases that require human judgment
- LLM grading failed or encountered errors

### Standard Deviation
Represents the variation in grades across different student submissions for each grader. Higher standard deviation indicates more spread in the scores (e.g., some very high and some very low scores).

## Troubleshooting

### API Key Error
```
ValueError: GEMINI_API_KEY environment variable not set
```
**Solution**: Set the `GEMINI_API_KEY` environment variable with your API key.

### Missing Columns Error
```
✗ Missing columns: Question 4.1 Response, Question 4.1 Score
```
**Solution**: Either rename your CSV columns to match the expected names, or update the column mappings in `sql_autograder/config.py`.

### Rate Limit Errors
If you encounter rate limiting errors from the Gemini API:
1. Increase the delay: `--rate-limit 2.0` or higher
2. Process fewer students at a time: `--max-students 50`
3. Check your API quota at https://makersuite.google.com/

### JSON Parsing Errors
The system automatically retries failed API calls up to 3 times. If issues persist:
1. Verify your API key is valid
2. Ensure you have sufficient API quota
3. Check the error messages in the console output
4. Try with a smaller batch (`--max-students 10`) to test

### File Not Found
```
Error loading CSV: [Errno 2] No such file or directory: 'submissions.csv'
```
**Solution**: Make sure the CSV file path is correct. Use absolute paths if needed.

## Command Reference

### Grade Command
```bash
python main.py grade <input_csv> [options]

Options:
  --output OUTPUT          Output CSV file (default: output/grading_results.csv)
  --max-students N         Grade only first N students
  --rate-limit SECONDS     Delay between API calls (default: 1.0)
```

### Stats Command
```bash
python main.py stats <results_csv> [options]

Options:
  --output OUTPUT          Output text file (default: output/statistics_report.txt)
```

### Grader-Stats Command
```bash
python main.py grader-stats <results_csv> [options]

Options:
  --output OUTPUT          Output text file (default: output/per_grader_statistics.txt)
```

### Visualize Command
```bash
python main.py visualize <results_csv> [options]

Options:
  --output-dir DIR         Output directory (default: output/)
```

## Dependencies

- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical operations
- `google-generativeai>=0.3.0` - Gemini API
- `matplotlib>=3.7.0` - Visualizations