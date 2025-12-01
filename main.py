#!/usr/bin/env python3
"""
Main entry point for SQL Autograder.
Command-line interface for grading submissions and generating statistics.
"""

import argparse
import time
from pathlib import Path

from sqlAutograder import (
    get_gemini_config,
    get_grading_config,
    GeminiGrader,
    SubmissionLoader,
    ResultsProcessor,
    GradingStatistics,
    GradingVisualizer
)


def grade_submissions(
    input_csv: str,
    output_csv: str = None,
    max_students: int = None,
    rate_limit_delay: float = 1.0
) -> bool:
    """
    Grade student submissions and save results.
    
    Args:
        input_csv: Path to input CSV with submissions
        output_csv: Path to save grading results (default: output/grading_results.csv)
        max_students: Maximum number of students to grade (None for all)
        rate_limit_delay: Delay between API calls in seconds
        
    Returns:
        bool: True if successful
    """
    # Create output directory and use default filename if not provided
    if output_csv is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_csv = str(output_dir / "grading_results.csv")
    
    print("=" * 60)
    print("SQL AUTOGRADER")
    print("=" * 60)
    print()
    
    # Load configurations
    try:
        print("1. Loading configuration...")
        gemini_config = get_gemini_config()
        grading_config = get_grading_config()
        print(f"   ✓ Using model: {gemini_config.model_name}")
        print()
    except ValueError as e:
        print(f"   ✗ Configuration error: {e}")
        return False
    
    # Load submissions
    print("2. Loading submissions...")
    loader = SubmissionLoader(input_csv, grading_config.question_columns)
    
    if not loader.load():
        print("   ✗ Failed to load CSV file")
        return False
    
    print(f"   ✓ Loaded {loader.get_count()} submissions")
    
    # Validate columns
    missing_cols = loader.validate_columns()
    if missing_cols:
        print(f"   ✗ Missing columns: {', '.join(missing_cols)}")
        return False
    
    print("   ✓ All required columns present")
    print()
    
    # Initialize grader
    print("3. Initializing Gemini grader...")
    grader = GeminiGrader(gemini_config)
    print("   ✓ Grader initialized")
    print()
    
    # Process submissions
    submissions = loader.get_submissions(max_students)
    total = len(submissions)
    
    print(f"4. Grading {total} submissions...")
    print()
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, submission in enumerate(submissions, 1):
        print(f"--- Student {i}/{total} ---")
        print(f"Name: {submission.student_name}")
        print(f"ID: {submission.student_id}")
        
        # Display grader scores
        for q_num in grading_config.questions:
            score = submission.grader_scores[q_num]
            print(f"Q{q_num} Grader Score: {score}/10")
        
        # Grade with LLM
        llm_result, error = grader.grade_student_submission(submission.queries)
        
        if llm_result:
            # Successful grading
            result = ResultsProcessor.create_result_from_grading(
                submission.student_id,
                submission.student_name,
                submission.queries,
                submission.grader_scores,
                llm_result,
                grading_config.questions
            )
            
            # Display LLM scores
            for q_num in grading_config.questions:
                q_prefix = f'q{q_num.replace(".", "_")}'
                llm_score = getattr(result, f'{q_prefix}_llm_score')
                diff = getattr(result, f'{q_prefix}_score_difference')
                print(f"  Q{q_num}: LLM={llm_score:.1f}/10, Diff={diff:+.1f}")
            
            print(f"  Total: LLM={result.total_llm_score:.1f}/50, "
                  f"Grader={result.total_grader_score}/50, "
                  f"Diff={result.total_score_difference:+.1f}")
            
            success_count += 1
        else:
            # Failed grading
            print(f"  ✗ Grading failed: {error}")
            result = ResultsProcessor.create_failed_result(
                submission.student_id,
                submission.student_name,
                submission.queries,
                submission.grader_scores,
                grading_config.questions
            )
            fail_count += 1
        
        results.append(result)
        print()
        
        # Rate limiting
        if i < total:
            time.sleep(rate_limit_delay)
    
    # Save results
    print("=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)
    print()
    
    if ResultsProcessor.save_results_to_csv(results, output_csv):
        print(f"✓ Results saved to: {output_csv}")
    else:
        print(f"✗ Failed to save results")
        return False
    
    # Summary
    print()
    print("=" * 60)
    print("GRADING SUMMARY")
    print("=" * 60)
    print(f"Total students: {total}")
    print(f"Successfully graded: {success_count}")
    print(f"Failed: {fail_count}")
    print()
    
    return True


def generate_statistics(results_csv: str, output_txt: str = None) -> bool:
    """
    Generate statistics report from grading results.
    
    Args:
        results_csv: Path to grading results CSV
        output_txt: Path to save statistics report (default: output/statistics_report.txt)
        
    Returns:
        bool: True if successful
    """
    # Create output directory and use default filename if not provided
    if output_txt is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_txt = str(output_dir / "statistics_report.txt")
    
    print("=" * 60)
    print("GENERATING STATISTICS")
    print("=" * 60)
    print()
    
    stats = GradingStatistics(results_csv)
    
    if not stats.load_and_validate():
        print("✗ Failed to load results")
        return False
    
    print(f"✓ Loaded results for analysis")
    print()
    
    if stats.save_report(output_txt):
        print(f"✓ Statistics saved to: {output_txt}")
        
        # Also print to console
        print()
        print(stats.generate_report())
        return True
    else:
        print("✗ Failed to save statistics")
        return False
    
def generate_per_grader_statistics(results_csv: str, output_txt: str = None) -> bool:
    """
    Generate per-grader statistics report from grading results.
    
    Args:
        results_csv: Path to grading results CSV
        output_txt: Path to save statistics report (default: output/per_grader_statistics.txt)
        
    Returns:
        bool: True if successful
    """
    # Create output directory and use default filename if not provided
    if output_txt is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_txt = str(output_dir / "per_grader_statistics.txt")
    
    print("=" * 60)
    print("GENERATING PER-GRADER STATISTICS")
    print("=" * 60)
    print()
    
    stats = GradingStatistics(results_csv)
    
    if not stats.load_and_validate():
        print("✗ Failed to load results")
        return False
    
    print(f"✓ Loaded results for analysis")
    print()
    
    if stats.save_per_grader_report(output_txt):
        print(f"✓ Per-grader statistics saved to: {output_txt}")
        
        # Also print to console
        print()
        print(stats.generate_per_grader_report())
        return True
    else:
        print("✗ Failed to save per-grader statistics")
        return False
    
def generate_visualizations(results_csv: str, output_dir: str = "output") -> bool:
    """
    Generate visualization plots from grading results.
    
    Args:
        results_csv: Path to grading results CSV
        output_dir: Directory to save visualizations
        
    Returns:
        bool: True if successful
    """    
    print("=" * 60)
    print("GENERATING VISUALIZATIONS")
    print("=" * 60)
    print()
    
    visualizer = GradingVisualizer(results_csv)
    
    print("Creating overall distribution plot...")
    visualizer.plot_overall_distribution(f"{output_dir}/overall_distribution.png")
    
    print("\nCreating per-grader distribution plots...")
    visualizer.plot_per_grader_distributions(output_dir)
    
    print("\nCreating all-graders grid plot...")
    visualizer.plot_all_graders_grid(f"{output_dir}/all_graders_grid.png")
    
    print()
    print("=" * 60)
    print("VISUALIZATIONS COMPLETE")
    print("=" * 60)
    print(f"\nCheck the '{output_dir}/' folder for:")
    print("  - overall_distribution.png")
    print("  - G1_distribution.png through G6_distribution.png")
    print("  - all_graders_grid.png")
    print()
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='SQL Autograder - LLM-based SQL grading system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Grade all submissions (creates output/grading_results.csv)
  python main.py grade exam1-submission.csv
  
  # Generate overall statistics (creates output/statistics_report.txt)
  python main.py stats output/grading_results.csv
  
  # Generate per-grader statistics (creates output/per_grader_statistics.txt)
  python main.py grader-stats output/grading_results.csv
  
  # Grade with custom output name
  python main.py grade exam1-submission.csv --output my_results.csv
  
  # Grade first 50 submissions
  python main.py grade exam1-submission.csv --max-students 50

Environment Variables:
  GEMINI_API_KEY          Your Google Gemini API key (required)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Grade command
    grade_parser = subparsers.add_parser('grade', help='Grade student submissions')
    grade_parser.add_argument('input_csv', help='Input CSV file with submissions')
    grade_parser.add_argument(
        '--output',
        help='Output CSV file for results (default: output/grading_results.csv)'
    )
    grade_parser.add_argument(
        '--max-students',
        type=int,
        help='Maximum number of students to grade (default: all)'
    )
    grade_parser.add_argument(
        '--rate-limit',
        type=float,
        default=1.0,
        help='Delay between API calls in seconds (default: 1.0)'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Generate overall statistics report')
    stats_parser.add_argument('results_csv', help='Input CSV file with grading results')
    stats_parser.add_argument(
        '--output',
        help='Output text file for statistics (default: output/statistics_report.txt)'
    )
    
    # Per-grader stats command
    grader_stats_parser = subparsers.add_parser('grader-stats', help='Generate per-grader statistics report')
    grader_stats_parser.add_argument('results_csv', help='Input CSV file with grading results')
    grader_stats_parser.add_argument(
        '--output',
        help='Output text file for statistics (default: output/per_grader_statistics.txt)'
    )
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualization plots')
    viz_parser.add_argument('results_csv', help='Input CSV file with grading results')
    viz_parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for plots (default: output/)'
    )
    args = parser.parse_args()
    
    if args.command == 'grade':
        success = grade_submissions(
            args.input_csv,
            args.output,
            args.max_students,
            args.rate_limit
        )
        exit(0 if success else 1)
    
    elif args.command == 'stats':
        success = generate_statistics(args.results_csv, args.output)
        exit(0 if success else 1)
    
    elif args.command == 'grader-stats':
        success = generate_per_grader_statistics(args.results_csv, args.output)
        exit(0 if success else 1)

    elif args.command == 'visualize':
        success = generate_visualizations(args.results_csv, args.output_dir)
        exit(0 if success else 1)
    
    else:
        parser.print_help()
        exit(1)


if __name__ == '__main__':
    main()