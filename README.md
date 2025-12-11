# SQL Autograder

An LLM-based SQL grading system that automatically grades student SQL submissions and compares with human grader scores. Supports both Google Gemini API and local Ollama models.

## Features

- **Automated Grading**: Uses Google Gemini API or local Ollama models to grade SQL submissions based on detailed rubrics
- **Multiple Model Support**: Gemini (API) and Ollama models (Llama, DeepSeek-R1, Mistral, etc.)
- **Comprehensive Analysis**: Compares LLM grading with human grader scores
- **Detailed Feedback**: Provides specific feedback and identifies submissions needing manual review
- **Per-Grader Statistics**: Analyzes grading patterns for each human grader (G1-G6)
- **Visualizations**: Generates distribution plots comparing LLM and human grading
- **Modular Design**: Clean, maintainable code structure with separate modules
- **Easy Configuration**: Simple setup via environment variables
- **Organized Output**: Results organized by model in separate folders

## Project Structure
```
.
├── sqlAutograder/           # Main package
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management
│   ├── prompts.py          # Grading prompts and rubrics
│   ├── grader.py           # LLM grading logic (Gemini API)
│   ├── ollama_grader.py    # LLM grading logic (Ollama local models)
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
- Google Gemini API key ([get one here](https://aistudio.google.com/api-keys)) for Gemini model
- Ollama ([install here](https://ollama.com)) for local models

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key (if using Gemini):

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

### Ollama Setup (for local models)

1. Install Ollama:
```bash
brew install ollama
```

2. Start the Ollama server:
```bash
ollama serve
```

3. Pull a model:
```bash
# Recommended
ollama pull llama3.1:8b

# Other options
ollama pull llama3.2:3b      # Faster, smaller
ollama pull deepseek-r1      # Reasoning model
ollama pull mistral          
ollama pull qwen2.5:7b       
```

## Usage

### Complete Workflow
```bash
# 1. Set API key (once per terminal session) - only needed for Gemini
export GEMINI_API_KEY='your-api-key-here'

# 2. Grade submissions with Gemini (default)
python main.py grade exam1-submission.csv

# 2. Or grade with a local Ollama model
python main.py grade exam1-submission.csv --model llama3.1:8b

# 3. Generate overall statistics
python main.py stats output/gemini/grading_results.csv

# 4. Generate per-grader statistics
python main.py grader-stats output/gemini/grading_results.csv

# 5. Generate visualizations
python main.py visualize output/gemini/grading_results.csv
```

### 1. Grading Student Submissions

**With Gemini (default):**
```bash
python main.py grade exam1-submission.csv
```
Creates: `output/gemini/grading_results.csv`

**With Ollama models:**
```bash
# Llama 3.1 8B (recommended for local)
python main.py grade exam1-submission.csv --model llama3.1:8b

# Llama 3.2 3B (faster, less accurate)
python main.py grade exam1-submission.csv --model llama3.2:3b

# DeepSeek-R1 (reasoning model, slower)
python main.py grade exam1-submission.csv --model deepseek-r1
```
Creates: `output/llama3-1-8b/grading_results.csv` (folder named after model)

**With options:**
```bash
# Custom output filename
python main.py grade exam1-submission.csv --output my_results.csv

# Grade only first 50 students (for testing)
python main.py grade exam1-submission.csv --max-students 50

# Adjust rate limiting (delay between API calls in seconds)
python main.py grade exam1-submission.csv --rate-limit 2.0

# Combine options
python main.py grade exam1-submission.csv --model llama3.1:8b --max-students 100 --rate-limit 1.5
```

### 2. Generating Overall Statistics

**Basic usage:**
```bash
python main.py stats output/gemini/grading_results.csv
```
Creates: `output/gemini/statistics_report_gemini.txt`

**With custom output:**
```bash
python main.py stats output/gemini/grading_results.csv --output my_stats.txt
```

**Output includes:**
- Summary statistics (total students, averages, standard deviations)
- Overall agreement rate between LLM and human graders
- Per-question statistics and agreement rates
- Detailed breakdown for each of the 5 SQL questions

### 3. Generating Per-Grader Statistics

**Basic usage:**
```bash
python main.py grader-stats output/gemini/grading_results.csv
```
Creates: `output/gemini/per_grader_statistics_gemini.txt`

**With custom output:**
```bash
python main.py grader-stats output/gemini/grading_results.csv --output grader_analysis.txt
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
python main.py visualize output/gemini/grading_results.csv
```

**With custom output directory:**
```bash
python main.py visualize output/gemini/grading_results.csv --output-dir plots/
```

**Generated files:**
- `overall_distribution_<model>.png` - Side-by-side comparison of Human vs LLM grade distribution
- `G1_distribution_<model>.png` through `G6_distribution_<model>.png` - Individual grader comparisons
- `all_graders_grid_<model>.png` - Grid view of all 6 graders

Each visualization shows:
- Human grader distribution on the left
- LLM grader distribution on the right
- Count labels on each bar
- Statistics (N, mean, standard deviation, difference)

## Output Structure

Results are organized by model:
```
output/
├── gemini/
│   ├── grading_results.csv
│   ├── statistics_report_gemini.txt
│   ├── per_grader_statistics_gemini.txt
│   ├── overall_distribution_gemini.png
│   ├── G1_distribution_gemini.png
│   ├── ...
│   └── all_graders_grid_gemini.png
├── llama3-1-8b/
│   └── (same structure)
└── deepseek-r1/
    └── (same structure)
```

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

**Note**: If your CSV has different column names, update them in `sqlAutograder/config.py` in the `get_grading_config()` function.

## Output Files

### 1. Grading Results CSV (`output/<model>/grading_results.csv`)

Contains detailed grading information for each student:
- Student ID and name
- SQL queries submitted for each question
- Human grader scores (0-10 per question)
- LLM scores (0-10 per question)
- Score differences (LLM - Human)
- Feedback for each question
- Flags indicating if manual review is needed
- Total scores (out of 50 points)

### 2. Statistics Report (`output/<model>/statistics_report_<model>.txt`)

Overall statistics including:
- Summary statistics across all students
- Question-level agreement rates
- Per-question detailed analysis
- Average scores and standard deviations

### 3. Per-Grader Statistics (`output/<model>/per_grader_statistics_<model>.txt`)

Grader-specific analysis including:
- Total scores by grader
- Per-question breakdown for each grader
- Agreement rates for each grader
- Comparison of grading patterns

### 4. Visualizations (`output/<model>/*_<model>.png`)

- **overall_distribution_<model>.png**: Overall comparison of all students
- **G1-G6_distribution_<model>.png**: Individual grader comparisons
- **all_graders_grid_<model>.png**: Grid view of all graders

## Customizing for Your Questions

### Changing Question Numbers or Column Names

Edit `sqlAutograder/config.py`:
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

Edit `sqlAutograder/prompts.py`:

1. Update the database schema in the prompt
2. Modify question descriptions
3. Change correct answers
4. Adjust deduction rules

The prompt is well-structured and clearly commented for easy modification.

### Configuration Settings

Edit `sqlAutograder/config.py` to adjust model and grading settings:

**Gemini Configuration (`GeminiConfig`):**
```python
model_name: str = "gemini-2.5-flash"  # Gemini model to use
temperature: float = 0.0              # 0 = deterministic, higher = more random
max_retries: int = 3                  # Retry attempts on API failure
retry_delay: float = 2.0              # Seconds between retries
```

**Ollama Configuration (`OllamaConfig`):**
```python
model_name: str = "llama3.1:8b"       # Default Ollama model
base_url: str = "http://localhost:11434"  # Ollama server URL
temperature: float = 0.0              # 0 = deterministic, higher = more random
max_tokens: int = 4096                # Max response length
max_retries: int = 3                  # Retry attempts on failure
retry_delay: float = 2.0              # Seconds between retries
timeout: float = 300.0                # Request timeout (seconds)
```

**When to adjust:**
- Increase `timeout` if grading is timing out on slower hardware
- Increase `max_retries` if you're seeing intermittent failures
- Adjust `temperature` if you want more varied responses (not recommended for grading)
- Change `base_url` if running Ollama on a different machine

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

### Ollama Connection Error
```
Ollama server not running. Start it with: ollama serve
```
**Solution**: Open a terminal and run `ollama serve`, then try again.

### Ollama Model Not Found
```
Error: model 'llama3.1:8b' not found
```
**Solution**: Pull the model first: `ollama pull llama3.1:8b`

### JSON Parsing Errors (Ollama)
Some smaller models (like Llama 3.2 3B) may not consistently return valid JSON.
**Solution**: Use Llama 3.1 8B or larger models for better JSON compliance.

### Missing Columns Error
```
✗ Missing columns: Question 4.1 Response, Question 4.1 Score
```
**Solution**: Either rename your CSV columns to match the expected names, or update the column mappings in `sqlAutograder/config.py`.

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
  --output OUTPUT          Output CSV file (default: output/<model>/grading_results.csv)
  --max-students N         Grade only first N students
  --rate-limit SECONDS     Delay between API calls (default: 1.0)
  --model MODEL            Model to use: "gemini" or Ollama model name (default: gemini)
```

### Stats Command
```bash
python main.py stats <results_csv> [options]

Options:
  --output OUTPUT          Output text file (default: same directory as input)
```

### Grader-Stats Command
```bash
python main.py grader-stats <results_csv> [options]

Options:
  --output OUTPUT          Output text file (default: same directory as input)
```

### Visualize Command
```bash
python main.py visualize <results_csv> [options]

Options:
  --output-dir DIR         Output directory (default: same directory as input)
```

## Dependencies

- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical operations
- `google-generativeai>=0.3.0` - Gemini API
- `matplotlib>=3.7.0` - Visualizations
- `requests>=2.28.0` - Ollama API calls