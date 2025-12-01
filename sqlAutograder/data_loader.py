"""
Data processing module for handling student submissions.
"""

import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StudentSubmission:
    """Represents a single student's submission."""
    student_id: str
    student_name: str
    queries: Dict[str, str]
    grader_scores: Dict[str, float]


class SubmissionLoader:
    """Handles loading and processing student submissions from CSV."""
    
    def __init__(self, csv_path: str, question_columns: Dict[str, Dict[str, str]]):
        """
        Initialize submission loader.
        
        Args:
            csv_path: Path to the CSV file with submissions
            question_columns: Mapping of question numbers to column names
        """
        self.csv_path = csv_path
        self.question_columns = question_columns
        self.df: Optional[pd.DataFrame] = None
    
    def load(self) -> bool:
        """
        Load the CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.df = pd.read_csv(self.csv_path)
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def validate_columns(self) -> List[str]:
        """
        Validate that all required columns exist.
        
        Returns:
            List of missing column names (empty if all present)
        """
        if self.df is None:
            return ["CSV not loaded"]
        
        missing = []
        
        # Check for Student ID and Name columns
        if 'Student ID' not in self.df.columns:
            missing.append('Student ID')
        if 'Name' not in self.df.columns:
            missing.append('Name')
        
        # Check for question columns
        for q_num, cols in self.question_columns.items():
            if cols['response'] not in self.df.columns:
                missing.append(f"{q_num} Response")
            if cols['score'] not in self.df.columns:
                missing.append(f"{q_num} Score")
        
        return missing
    
    def get_submissions(self, max_count: Optional[int] = None) -> List[StudentSubmission]:
        """
        Get student submissions from the loaded data.
        
        Args:
            max_count: Maximum number of submissions to return (None for all)
            
        Returns:
            List of StudentSubmission objects
        """
        if self.df is None:
            return []
        
        df_to_process = self.df.head(max_count) if max_count else self.df
        submissions = []
        
        for _, row in df_to_process.iterrows():
            queries = {}
            grader_scores = {}
            
            for q_num, cols in self.question_columns.items():
                query = row[cols['response']]
                score = row[cols['score']]
                
                # Handle empty/missing queries
                if pd.isna(query) or str(query).strip() == "":
                    query = "[NO ANSWER PROVIDED]"
                
                queries[q_num] = str(query)
                grader_scores[q_num] = float(score) if not pd.isna(score) else 0.0
            
            submissions.append(StudentSubmission(
                student_id=str(row['Student ID']),
                student_name=str(row['Name']),
                queries=queries,
                grader_scores=grader_scores
            ))
        
        return submissions
    
    def get_count(self) -> int:
        """
        Get the total number of submissions in the loaded data.
        
        Returns:
            Number of submissions
        """
        return len(self.df) if self.df is not None else 0