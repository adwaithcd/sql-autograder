"""
LLM-based grading module using Google Gemini API.
"""

import json
import time
from typing import Dict, Optional, Tuple
import google.generativeai as genai

from .config import GeminiConfig
from .prompts import create_grading_prompt


class GeminiGrader:
    """Handles LLM-based grading using Google Gemini API."""
    
    def __init__(self, config: GeminiConfig):
        """
        Initialize the Gemini grader.
        
        Args:
            config: Gemini API configuration
        """
        self.config = config
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model_name)
        self.generation_config = genai.types.GenerationConfig(
            temperature=config.temperature
        )
    
    def grade_student_submission(
        self, 
        student_queries: Dict[str, str]
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Grade a student's submission for all questions.
        
        Args:
            student_queries: Dictionary mapping question numbers to SQL queries
            
        Returns:
            Tuple of (grading_result, error_message)
            - grading_result: Dictionary with scores and feedback if successful
            - error_message: Error description if grading failed
        """
        prompt = create_grading_prompt(student_queries)
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                result = self._parse_response(response.text)
                return result, None
                
            except json.JSONDecodeError as e:
                error_msg = f"JSON parsing error on attempt {attempt + 1}: {str(e)}"
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    return None, error_msg
                    
            except Exception as e:
                error_msg = f"Grading error on attempt {attempt + 1}: {str(e)}"
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    return None, error_msg
        
        return None, "Max retries exceeded"
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse and clean the LLM response.
        
        Args:
            response_text: Raw response text from LLM
            
        Returns:
            Dictionary with parsed grading results
            
        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        # Clean markdown code blocks if present
        cleaned_text = response_text.strip()
        
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
            
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        cleaned_text = cleaned_text.strip()
        
        return json.loads(cleaned_text)
    
    @staticmethod
    def create_failed_result(
        question_numbers: list[str],
        error_message: str = "Grading failed"
    ) -> Dict:
        """
        Create a result dictionary for failed grading attempts.
        
        Args:
            question_numbers: List of question numbers
            error_message: Error description
            
        Returns:
            Dictionary with -1 scores and error information
        """
        result = {}
        
        for q_num in question_numbers:
            q_key = f'question_{q_num.replace(".", "_")}'
            result[q_key] = {
                'score': -1,
                'deduction_details': error_message,
                'feedback': 'Automatic grading failed - requires manual review',
                'needs_review': True
            }
        
        return result