"""
Lab evaluation endpoint with rubric-based scoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from llm.provider_factory import get_llm_provider

router = APIRouter(prefix="/v1", tags=["labs"])


class FileSubmission(BaseModel):
    path: Optional[str] = ""
    content: Optional[str] = ""


class RubricCriterion(BaseModel):
    name: Optional[str] = ""
    weight: Optional[int] = 0  # points
    description: Optional[str] = ""


class EvaluateRequest(BaseModel):
    files: Optional[List[FileSubmission]] = []
    rubric: Optional[Dict[str, int]] = {}  # {"correctness": 30, "style": 20, ...}
    rubric_descriptions: Optional[Dict[str, str]] = None


class CriterionResult(BaseModel):
    criterion: str
    score: str  # "Met", "Partial", "Not Met"
    points: int
    max_points: int
    feedback: str


class EvaluateResponse(BaseModel):
    rubric: List[CriterionResult]
    overall_score: int
    overall_max: int
    percentage: float
    summary: str


EVALUATOR_PROMPT = """You are an objective code evaluator for student lab assignments.

EVALUATION RULES:
1. Be FAIR and CONSTRUCTIVE
2. Provide SPECIFIC feedback with examples
3. Score as: "Met" (100%), "Partial" (50-70%), "Not Met" (0-30%)
4. Focus on learning, not punishment
5. Highlight what's good AND what needs work

RUBRIC CRITERIA:
{rubric_text}

CODE SUBMISSION:
{code_text}

For each criterion, provide:
{{
    "criterion": "name",
    "score": "Met|Partial|Not Met",
    "feedback": "specific, actionable feedback"
}}

Return JSON array of evaluations.
"""


@router.post("/labs/evaluate", response_model=EvaluateResponse)
async def evaluate_lab(request: EvaluateRequest):
    """
    Evaluate student lab submission against rubric
    """
    try:
        # Validate inputs - return helpful response instead of error
        if not request.files or len(request.files) == 0:
            return EvaluateResponse(
                rubric=[],
                overall_score=0,
                overall_max=0
            )
        
        if not request.rubric or len(request.rubric) == 0:
            return EvaluateResponse(
                rubric=[],
                overall_score=0,
                overall_max=0
            )
        
        # Build rubric text
        rubric_text = ""
        for criterion, points in request.rubric.items():
            desc = request.rubric_descriptions.get(criterion, "") if request.rubric_descriptions else ""
            rubric_text += f"\n- {criterion.upper()} ({points} points): {desc}"
        
        # Build code text
        code_text = ""
        for file in request.files:
            code_text += f"\n\nFile: {file.path}\n```\n{file.content}\n```"
        
        # Get provider
        provider = get_llm_provider()
        
        # Build prompt
        prompt = EVALUATOR_PROMPT.format(
            rubric_text=rubric_text,
            code_text=code_text
        )
        
        # Call LLM
        response = await provider.generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=1500
        )
        
        # Parse response with robust error handling
        import json
        try:
            evaluations = json.loads(response)
            if not isinstance(evaluations, list):
                raise ValueError("Expected list")
        except Exception:
            # Fallback - create safe default evaluations
            evaluations = [
                {
                    "criterion": criterion,
                    "score": "Partial",
                    "feedback": "Unable to evaluate automatically. Please review manually."
                }
                for criterion in request.rubric.keys()
            ]
        
        # Calculate scores
        results = []
        total_score = 0
        total_max = sum(request.rubric.values())
        
        for eval_item in evaluations:
            criterion = eval_item.get("criterion", "unknown")
            score_label = eval_item.get("score", "Partial")
            feedback = eval_item.get("feedback", "No feedback available")
            
            max_points = request.rubric.get(criterion, 0)
            
            # Convert score label to points
            if score_label == "Met":
                points = max_points
            elif score_label == "Partial":
                points = int(max_points * 0.6)  # 60%
            else:  # Not Met
                points = int(max_points * 0.2)  # 20%
            
            total_score += points
            
            results.append(CriterionResult(
                criterion=criterion,
                score=score_label,
                points=points,
                max_points=max_points,
                feedback=feedback
            ))
        
        percentage = (total_score / total_max * 100) if total_max > 0 else 0
        
        # Generate summary
        if percentage >= 80:
            summary = "Excellent work! Strong understanding demonstrated."
        elif percentage >= 60:
            summary = "Good effort. Review feedback for improvements."
        else:
            summary = "Needs significant work. Focus on fundamentals."
        
        return EvaluateResponse(
            rubric=results,
            overall_score=total_score,
            overall_max=total_max,
            percentage=round(percentage, 1),
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
