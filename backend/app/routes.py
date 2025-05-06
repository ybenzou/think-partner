from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
# 假设你的 gemini_client.py 文件在同一个目录下，且有一个 expand_with_gemini 函数
# expand_with_gemini(prompt: str) -> List[str]
from .gemini_client import expand_with_gemini
import os

router = APIRouter()

class ExpandRequest(BaseModel):
    # context 是完整的路径，例如 "初始疑问 -> 计划 A -> 步骤 1"
    context: str
    # question 是当前被展开节点的 label，例如 "步骤 1"
    question: str

class ExpandResponse(BaseModel):
    ideas: List[str] # 期望返回 2-3 个字符串作为新的子节点 label

# 用于判断是否为初始展开的辅助函数 (保持不变)
def is_initial_expansion(context: str, question: str) -> bool:
    """
    Checks if the context indicates this is the initial expansion of the root node.
    In the frontend logic provided, the initial node's context path is just its label.
    """
    return context.strip() == question.strip()

@router.post("/api/llm_expand", response_model=ExpandResponse)
def llm_expand(req: ExpandRequest):
    """
    Expands a thinking node using an LLM based on the current context path.
    Generates distinct initial plans or diverse sub-steps/angles for subsequent nodes.
    """
    print(f"Received expand request: Context='{req.context}', Question='{req.question}'")

    if is_initial_expansion(req.context, req.question):
        # 初始展开：生成总体计划，强调多样性和不同切入点
        prompt_text = f"""
You are a high-level problem-solving architect. Your role is to help break down complex problems into foundational, distinct approaches.

The central question or problem to address is: "{req.question}"

Please propose 2 to 3 fundamentally **different and high-level overall plans or strategies** to approach this problem. Each plan should represent a unique direction or perspective for solving the problem.
List each plan as a single line item. Avoid numbering or introductory/concluding text. Focus purely on clear, distinct plan titles.
Example (for "How to improve customer satisfaction?"):
Focus on product quality improvements
Enhance customer service interaction
Optimize post-purchase follow-up process
"""
    else:
        # 后续展开：针对当前步骤生成更详细的、不同角度的下一步骤或思考方向
        prompt_text = f"""
You are a detailed problem-solving assistant, specializing in exploring different facets of a specific step within a plan.

We are currently operating within this plan/path:
{req.context}

The specific step we are focusing on is: "{req.question}"

Considering the overall path and the current step, please suggest 2 to 3 **distinct and detailed next steps, sub-problems, or different angles** to explore specifically for "{req.question}". Each suggestion should offer a clear, different way to break down or act on this particular step.
List each suggestion as a single line item. Avoid numbering or introductory/concluding text. Focus purely on clear, actionable next steps or sub-topics.
Example (for path "Improve Website Traffic -> Improve SEO", detailing step "Optimize on-page content"):
Focus on technical SEO aspects of pages
Focus on content quality and relevance
Focus on user experience signals (dwell time, bounce rate)
"""

    print("➡️ Sending prompt to Gemini:")
    print(prompt_text)

    try:
        # Call your Gemini client function
        ideas = expand_with_gemini(prompt_text)

        # Basic validation and parsing (essential if gemini_client doesn't guarantee List[str])
        if not isinstance(ideas, list):
            print(f"❌ Warning: expand_with_gemini did not return a list. Received type: {type(ideas)}. Attempting to parse.")
            if isinstance(ideas, str):
                 # Try splitting by newline if it's a single string
                 ideas = [line.strip() for line in ideas.strip().split('\n') if line.strip()]
            else:
                 ideas = [] # Fallback to empty if parsing fails

        # Ensure all items in the list are strings after parsing attempt
        ideas = [str(item).strip() for item in ideas if item is not None]
        ideas = [item for item in ideas if item] # Remove empty strings

        # Ensure we return at most 3 ideas, matching the prompt's request
        ideas = ideas[:3]

        print("✅ Final response to frontend:", ideas)
        return {"ideas": ideas}

    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        # In a production app, you might want to return a specific error status code
        # raise HTTPException(status_code=500, detail=f"LLM API error: {e}")
        return {"ideas": []} # Return empty list on error for frontend robustness