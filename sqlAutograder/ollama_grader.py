"""
LLM-based grading module using Ollama for local models.
Supports DeepSeek-R1, Llama, and other Ollama-compatible models.
"""

import json
import re
import time
import requests
from typing import Dict, Optional, Tuple

from .config import OllamaConfig
from .prompts import create_grading_prompt


class OllamaGrader:
    """Handles LLM-based grading using local Ollama models."""
    
    def __init__(self, config: OllamaConfig):
        """
        Initialize the Ollama grader.
        
        Args:
            config: Ollama configuration
        """
        self.config = config
        self.api_url = f"{config.base_url}/api/generate"
    
    def _check_server(self) -> bool:
        """
        Check if Ollama server is running.
        
        Returns:
            bool: True if server is accessible
        """
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def _strip_thinking(self, text: str) -> str:
        """
        Remove <think>...</think> tags from R1 model output.
        
        Args:
            text: Raw response text
            
        Returns:
            Text with thinking tags removed
        """
        # Remove <think>...</think> blocks (handles multiline)
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return cleaned.strip()
    
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
        # First strip thinking tags (for R1 models)
        cleaned_text = self._strip_thinking(response_text)
        
        # Clean markdown code blocks if present
        if "```json" in cleaned_text:
            start = cleaned_text.find("```json") + 7
            end = cleaned_text.find("```", start)
            if end != -1:
                cleaned_text = cleaned_text[start:end]
        elif "```" in cleaned_text:
            start = cleaned_text.find("```") + 3
            end = cleaned_text.find("```", start)
            if end != -1:
                cleaned_text = cleaned_text[start:end]
        
        cleaned_text = cleaned_text.strip()
        
        # Try to find JSON object in the response
        # Look for the outermost { } pair
        first_brace = cleaned_text.find('{')
        last_brace = cleaned_text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            cleaned_text = cleaned_text[first_brace:last_brace + 1]
        
        return json.loads(cleaned_text)
    
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
        # Check if server is running
        if not self._check_server():
            return None, (
                "Ollama server not running. Start it with: ollama serve\n"
                "Then pull the model with: ollama pull " + self.config.model_name
            )
        
        prompt = create_grading_prompt(student_queries)
        
        for attempt in range(self.config.max_retries):
            try:
                # Make request to Ollama API
                response = requests.post(
                    self.api_url,
                    json={
                        "model": self.config.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.config.temperature,
                            "num_predict": self.config.max_tokens
                        }
                    },
                    timeout=self.config.timeout
                )
                
                if response.status_code != 200:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)
                        continue
                    return None, error_msg
                
                result_json = response.json()
                response_text = result_json.get("response", "")
                
                if not response_text:
                    error_msg = "Empty response from Ollama"
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay)
                        continue
                    return None, error_msg
                
                result = self._parse_response(response_text)
                return result, None
                
            except json.JSONDecodeError as e:
                # Debug: print the raw response that failed to parse
                print(f"\n  [DEBUG] Raw response (attempt {attempt + 1}):")
                print(f"  {response_text}...")  # First 500 chars
                print()
                error_msg = f"JSON parsing error on attempt {attempt + 1}: {str(e)}"
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    return None, error_msg
                    
            except requests.exceptions.Timeout:
                error_msg = f"Request timeout on attempt {attempt + 1}"
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