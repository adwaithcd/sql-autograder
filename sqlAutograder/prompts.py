"""
Prompt templates for SQL grading.
Contains the actual rubrics and instructions used for grading.
"""

from typing import Dict


def create_grading_prompt(student_queries: Dict[str, str]) -> str:
    """
    Create a comprehensive grading prompt for all SQL questions.
    
    Args:
        student_queries: Dictionary mapping question numbers to SQL queries
        
    Returns:
        str: Formatted grading prompt for the LLM
    """
    
    prompt = f"""You are an expert SQL grader, grading SQL queries for 5 questions. Each question is worth 10 points. Follow these rules consistently for ALL questions:

GENERAL GRADING INSTRUCTIONS:
1. ALWAYS check functional equivalence FIRST
   - If the query produces the correct logical result, give 10 points (full credit) immediately
   - Accept different syntax: JOIN vs comma-separated tables, different aliases, different ordering
   - Accept alternative correct approaches that achieve the same result
2. ONLY apply deductions if the query is NOT functionally equivalent
3. Be LENIENT - small syntax issues that don't break functionality should get minor or no deductions
4. Be CONSISTENT - same errors get same deductions across all students
5. Focus on logical correctness over syntax perfection

UNIVERSAL DEDUCTIONS (apply to all questions):
- Empty answer or "[NO ANSWER PROVIDED]": 0 points
- Query mostly wrong (completely wrong approach): 2-4 points maximum

DATABASE SCHEMA:
PART (P_PARTKEY, P_NAME, P_BRAND, P_TYPE, P_SIZE) key:P_PARTKEY
PARTSUPP (PS_PARTKEY, PS_SUPPKEY, PS_AVAILQTY, PS_SUPPLYCOST) key: PS_PARTKEY, PS_SUPPKEY
SUPPLIER (S_SUPPKEY, S_NAME, S_ADDRESS, S_PHONE, S_ACCTBAL) key: S_SUPPKEY

================================================================================
QUESTION 4.1: How many parts with size 1 or 4 are available?
================================================================================
STUDENT ANSWER: {student_queries['4.1']}

CORRECT ANSWERS (any of these):
1. SELECT SUM(ps_availqty) FROM Part, PartSupp WHERE ps_partkey = p_partkey AND (p_size=1 OR p_size=4);
2. SELECT count(DISTINCT p_partkey) FROM Part, PartSupp WHERE ps_partkey = p_partkey AND (p_size=1 OR p_size=4);
3. SELECT COUNT(*) FROM PART WHERE P_SIZE = 1 OR P_SIZE = 4;

SPECIFIC DEDUCTIONS (only if NOT functionally equivalent):
- Wrong column name (SIZE instead of P_SIZE): -1 point
- Missing PartSupp table: -2 points
- Missing join predicate: -3 points
- Wrong aggregation with wrong logic: -2 points
- Incorrect GROUP BY usage: -3 points
- Missing AND between WHERE predicates: -2 points
- Syntax errors that break functionality: -2 points

================================================================================
QUESTION 4.2: Return the distinct part brands (P_BRAND) of parts, which are supplied by Suppliers whose account balance (S_ACCTBAL) is smaller than 1000.
================================================================================
STUDENT ANSWER: {student_queries['4.2']}

CORRECT ANSWER:
SELECT DISTINCT p_brand FROM Part, PartSupp, Supplier 
WHERE p_partkey = ps_partkey AND ps_suppkey = s_suppkey AND s_acctbal < 1000

SPECIFIC DEDUCTIONS (only if NOT functionally equivalent):
- Missing DISTINCT: -1 point
- Missing join condition: -2 points per missing condition
- Missing required table: -2 points
- Wrong comparison operator (> instead of <): -1 point

================================================================================
QUESTION 4.3: Please return to me the number of distinct suppliers that supply each part. Results should show P_NAME, SUPPLIER_COUNT.
================================================================================
STUDENT ANSWER: {student_queries['4.3']}

CORRECT ANSWERS (any of these):
1. SELECT P_NAME, COUNT(*) FROM PARTSUPP, PART WHERE PS_PARTKEY=P_PARTKEY GROUP BY P_NAME
2. SELECT P_NAME, COUNT(DISTINCT PS_SUPPKEY) FROM PARTSUPP, PART WHERE PS_PARTKEY=P_PARTKEY GROUP BY P_NAME
3. Any explicit JOIN syntax variation of the above

SPECIFIC DEDUCTIONS (only if NOT functionally equivalent):
- Missing or wrong GROUP BY: -2 points
- Wrong aggregation but correct grouping: -1 point
- Missing join predicate: -2 points
- Missing required table: -2 points
- Minor syntax errors: -1 point

================================================================================
QUESTION 4.4: Please return to me the supplier that has the highest account balance (S_ACCTBAL).
================================================================================
STUDENT ANSWER: {student_queries['4.4']}

CORRECT ANSWERS (any of these):
1. SELECT S_SUPPKEY, S_NAME FROM SUPPLIER WHERE S_ACCTBAL = (SELECT MAX(S_ACCTBAL) FROM SUPPLIER);
2. SELECT S_NAME FROM SUPPLIER WHERE S_ACCTBAL = (SELECT MAX(S_ACCTBAL) FROM SUPPLIER);
3. SELECT * FROM SUPPLIER WHERE S_ACCTBAL = (SELECT MAX(S_ACCTBAL) FROM SUPPLIER);
4. SELECT * FROM SUPPLIER ORDER BY S_ACCTBAL DESC LIMIT 1;

SPECIFIC DEDUCTIONS (only if NOT functionally equivalent):
- Using LIMIT without ORDER BY: -1 point
- Logic errors but right approach: -2 points
- Missing MAX function in subquery approach: -2 points
- Syntax errors that break functionality: -2 points

================================================================================
QUESTION 4.5: Please return me the names of parts which have been supplied by at least two different suppliers.
================================================================================
STUDENT ANSWER: {student_queries['4.5']}

CORRECT ANSWERS (any of these):
1. SELECT P_NAME FROM PART P JOIN PARTSUPP PS ON P.P_PARTKEY = PS.PS_PARTKEY 
   GROUP BY P_NAME HAVING COUNT(DISTINCT PS.PS_SUPPKEY) >= 2;
2. SELECT DISTINCT P_NAME FROM PART, PARTSUPP PS1, PARTSUPP PS2 
   WHERE P_PARTKEY = PS1.PS_PARTKEY AND PS1.PS_PARTKEY = PS2.PS_PARTKEY 
   AND PS1.PS_SUPPKEY != PS2.PS_SUPPKEY;

SPECIFIC DEDUCTIONS (only if NOT functionally equivalent):
- Wrong GROUP BY but right idea: -1 point
- Missing HAVING clause in GROUP BY approach: -2 points
- Incorrect self-join conditions: -2 points
- Missing table aliases in self-join: -1 point

================================================================================
OUTPUT FORMAT
================================================================================
Return ONLY a JSON object (no markdown, no backticks, no extra text):
{{
    "question_4_1": {{
        "score": <0-10>,
        "deduction_details": "<specific deductions applied or 'Full credit'>",
        "feedback": "<brief explanation>",
        "needs_review": <true/false>
    }},
    "question_4_2": {{
        "score": <0-10>,
        "deduction_details": "<specific deductions applied or 'Full credit'>",
        "feedback": "<brief explanation>",
        "needs_review": <true/false>
    }},
    "question_4_3": {{
        "score": <0-10>,
        "deduction_details": "<specific deductions applied or 'Full credit'>",
        "feedback": "<brief explanation>",
        "needs_review": <true/false>
    }},
    "question_4_4": {{
        "score": <0-10>,
        "deduction_details": "<specific deductions applied or 'Full credit'>",
        "feedback": "<brief explanation>",
        "needs_review": <true/false>
    }},
    "question_4_5": {{
        "score": <0-10>,
        "deduction_details": "<specific deductions applied or 'Full credit'>",
        "feedback": "<brief explanation>",
        "needs_review": <true/false>
    }}
}}"""
    
    return prompt