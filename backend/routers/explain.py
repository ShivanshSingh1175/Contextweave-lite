"""
Progressive hint system endpoint
Provides 3 levels of hints: Conceptual, Logical, Line-by-line
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from llm.provider_factory import get_llm_provider

router = APIRouter(prefix="/v1", tags=["explain"])


class ExplainRequest(BaseModel):
    code: Optional[str] = ""
    level: Optional[int] = 1
    lang: str = "en"  # en or hi
    file_path: Optional[str] = None
    repo_context: Optional[dict] = None
    exam_mode: bool = False


class ExplainResponse(BaseModel):
    hint: str
    concepts: List[str]
    difficulty: int  # 1-5
    next_level_available: bool


TUTOR_SYSTEM_PROMPT = """You are ContextWeave Coach - a DISCIPLINED programming tutor, NEVER a solution generator.

MANDATORY RULES:
1. HINT LEVELS ONLY - never full solutions
   Level 1: CONCEPTUAL (high-level overview, what the code does)
   Level 2: LOGIC (step-by-step reasoning, algorithm breakdown)
   Level 3: LINE-BY-LINE (detailed explanation but NO copyable code)

2. ACADEMIC INTEGRITY:
   - Exam Mode: Level 1 hints ONLY
   - Always encourage reasoning
   - Suggest citations: "// Adapted from [concept] by [student name]"

3. MULTILINGUAL: Respond in {lang} for explanations, English for code/terms

4. ENCOURAGE REASONING: Ask "What do you think happens next?"

NEVER: Write complete functions, debug entire files, generate tests
ALWAYS: Scaffold thinking, surface misconceptions, track concepts

Output format:
- hint: Your explanation at the requested level
- concepts: Array of programming concepts (e.g., ["recursion", "binary-search"])
- difficulty: 1-5 rating
"""


def get_hint_prompt(code: str, level: int, lang: str, exam_mode: bool) -> str:
    """Generate prompt based on hint level"""
    
    lang_instruction = {
        "en": "Respond in clear, simple English.",
        "hi": "Respond in simple Hindi (Hinglish is okay for technical terms). Keep code terms in English."
    }
    
    level_instructions = {
        1: """Level 1 - CONCEPTUAL OVERVIEW:
- Explain WHAT this code does in 2-3 sentences
- Identify the main algorithm or pattern
- NO implementation details
- Example: "This implements binary search to find elements efficiently"
""",
        2: """Level 2 - LOGICAL BREAKDOWN:
- Explain HOW the code works step-by-step
- Break down the algorithm logic
- Explain key decisions and flow
- NO line-by-line code walkthrough
- Example: "First checks if array is empty, then compares middle element, recursively searches left or right half"
""",
        3: """Level 3 - DETAILED EXPLANATION:
- Explain line-by-line what each part does
- Clarify tricky parts and edge cases
- Explain variable purposes
- Still NO complete copyable solutions
- Example: "Line 5: `mid = (left + right) // 2` calculates the middle index to split the search space"
"""
    }
    
    if exam_mode and level > 1:
        level = 1
        exam_note = "\n⚠️ EXAM MODE ACTIVE: Providing only Level 1 conceptual hints."
    else:
        exam_note = ""
    
    prompt = f"""{TUTOR_SYSTEM_PROMPT.format(lang=lang)}

{lang_instruction[lang]}

{level_instructions[level]}

{exam_note}

CODE TO EXPLAIN:
```
{code}
```

Provide your response as JSON:
{{
    "hint": "your explanation here",
    "concepts": ["concept1", "concept2"],
    "difficulty": 1-5
}}
"""
    return prompt


@router.post("/explain", response_model=ExplainResponse)
async def explain_code(request: ExplainRequest):
    """
    Provide progressive hints for code understanding
    """
    try:
        # Debug logging
        print("DEBUG REQUEST:", request.dict())
        
        # Guard against empty code - return helpful message instead of error
        if not request.code or not request.code.strip():
            return ExplainResponse(
                hint="Please select some code to explain.",
                concepts=["general-programming"],
                difficulty=1,
                next_level_available=False
            )
        
        # Validate level
        if request.level not in [1, 2, 3]:
            request.level = 1  # Default to level 1 instead of throwing error
        
        # Validate language
        if request.lang not in ["en", "hi"]:
            request.lang = "en"  # Default to English instead of throwing error
        
        # Get LLM provider
        provider = get_llm_provider()
        
        # Build prompt
        prompt = get_hint_prompt(request.code, request.level, request.lang, request.exam_mode)
        
        # Call LLM
        response = await provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=800
        )
        
        # Debug logging
        print("DEBUG LLM RESPONSE:", response[:200] if response else "None")
        
        # Parse response with robust error handling
        import json
        try:
            result = json.loads(response)
            if not isinstance(result, dict):
                raise ValueError("Invalid JSON structure")
        except Exception:
            result = {
                "hint": str(response),
                "concepts": ["general-programming"],
                "difficulty": 3
            }
        
        return ExplainResponse(
            hint=result.get("hint", response),
            concepts=result.get("concepts", ["general-programming"]),
            difficulty=result.get("difficulty", 3),
            next_level_available=request.level < 3 and not request.exam_mode
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.post("/detect-concepts")
async def detect_concepts(code: str, file_path: Optional[str] = None):
    """
    Extract programming concepts from code for tagging
    """
    try:
        provider = get_llm_provider()
        
        prompt = f"""Analyze this code and extract programming concepts as tags.

CODE:
```
{code}
```

Return ONLY a JSON array of concept tags (lowercase, hyphenated):
["concept1", "concept2", ...]

Examples: ["recursion", "binary-search", "edge-cases", "arrays", "linked-lists"]
"""
        
        response = await provider.generate(prompt=prompt, temperature=0.2, max_tokens=200)
        
        import json
        try:
            concepts = json.loads(response)
            if not isinstance(concepts, list):
                raise ValueError("Expected list")
            return {"concepts": concepts}
        except Exception:
            # Fallback to safe default
            return {"concepts": ["general-programming"]}
        
    except Exception as e:
        return {"concepts": ["general-programming"]}
