"""
Context-aware tutoring chat endpoint
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.llm.provider_factory import get_provider

router = APIRouter(prefix="/v1", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[Dict] = None  # current_file, mastery data, etc.
    exam_mode: bool = False


class ChatResponse(BaseModel):
    message: str
    suggested_actions: List[str]


CHAT_SYSTEM_PROMPT = """You are ContextWeave Coach - a patient, encouraging programming tutor.

CORE PRINCIPLES:
1. NEVER provide complete solutions
2. Guide through QUESTIONS and HINTS
3. Encourage ACTIVE THINKING
4. Be SUPPORTIVE and PATIENT
5. Adapt to student's mastery level

CONVERSATION STYLE:
- Ask clarifying questions
- Break down complex problems
- Celebrate small wins
- Suggest next steps
- Use analogies and examples

FORBIDDEN:
- Writing complete functions
- Debugging entire files
- Generating test cases
- Doing homework for students

ENCOURAGED:
- "What do you think happens if...?"
- "Let's break this down step by step"
- "Good thinking! Now consider..."
- "That's a common misconception. Actually..."

{exam_mode_note}

Context about student:
{context_info}
"""


def build_context_info(context: Optional[Dict]) -> str:
    """Build context string from student data"""
    if not context:
        return "No context available."
    
    info = []
    
    if "current_file" in context:
        info.append(f"Working on: {context['current_file']}")
    
    if "mastery" in context:
        mastery = context["mastery"]
        weak_topics = [topic for topic, data in mastery.items() if data.get("score", 0) < 3]
        if weak_topics:
            info.append(f"Weak topics: {', '.join(weak_topics)}")
    
    if "recent_concepts" in context:
        info.append(f"Recently studied: {', '.join(context['recent_concepts'])}")
    
    return "\n".join(info) if info else "No context available."


@router.post("/chat", response_model=ChatResponse)
async def chat_tutor(request: ChatRequest):
    """
    Context-aware tutoring chat
    """
    try:
        # Build system prompt
        exam_mode_note = ""
        if request.exam_mode:
            exam_mode_note = "\n⚠️ EXAM MODE: Provide only conceptual guidance. No detailed hints."
        
        context_info = build_context_info(request.context)
        
        system_prompt = CHAT_SYSTEM_PROMPT.format(
            exam_mode_note=exam_mode_note,
            context_info=context_info
        )
        
        # Get provider
        provider = get_provider()
        
        # Build conversation
        conversation = f"{system_prompt}\n\n"
        for msg in request.messages[-5:]:  # Last 5 messages for context
            conversation += f"{msg.role.upper()}: {msg.content}\n"
        
        conversation += "\nASSISTANT:"
        
        # Call LLM
        response = await provider.generate(
            prompt=conversation,
            temperature=0.7,
            max_tokens=500
        )
        
        # Detect if student is asking for full solution
        user_message = request.messages[-1].content.lower()
        solution_keywords = ["write code", "give me code", "complete solution", "full code", "solve this"]
        
        if any(keyword in user_message for keyword in solution_keywords):
            response = "I can't write the complete solution for you, but I can guide you through it! Let's break down the problem step by step. What part are you stuck on?"
        
        # Generate suggested actions
        suggested_actions = []
        if "error" in user_message or "bug" in user_message:
            suggested_actions.append("Show me the specific error message")
        if "understand" in user_message or "explain" in user_message:
            suggested_actions.append("Select the confusing code and ask for hints")
        if "test" in user_message:
            suggested_actions.append("Try writing a simple test case first")
        
        return ChatResponse(
            message=response.strip(),
            suggested_actions=suggested_actions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/integrity-check")
async def check_integrity(code: str, student_history: Optional[Dict] = None):
    """
    Detect potential academic integrity issues
    """
    try:
        signals = []
        
        # Check code length
        if len(code) > 500:
            signals.append("large_code_block")
        
        # Check complexity (simple heuristic)
        if code.count("def ") > 5 or code.count("class ") > 2:
            signals.append("high_complexity")
        
        # Check for common copy-paste patterns
        if "# TODO" in code or "# FIXME" in code:
            signals.append("template_code")
        
        # Generate response
        if len(signals) >= 2:
            message = "This solution looks quite complete! Want to walk through your reasoning step by step? It helps to explain your thought process."
            severity = "medium"
        elif len(signals) == 1:
            message = "Good progress! Make sure you understand each part of your code."
            severity = "low"
        else:
            message = "Keep up the good work!"
            severity = "none"
        
        return {
            "signals": signals,
            "message": message,
            "severity": severity,
            "suggestion": "Consider adding comments explaining your approach: // My approach: [explain]"
        }
        
    except Exception as e:
        return {
            "signals": [],
            "message": "Unable to check integrity",
            "severity": "none"
        }
