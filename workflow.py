from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from github_tools import get_repo_file_content, create_github_pr

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

class PRState(TypedDict):
    repo_name: str
    filepath: str
    issue_description: str
    original_code: str
    fixed_code: str
    pr_title: str
    pr_body: str
    status_msg: str

def fetch_code_node(state: PRState):
    res = get_repo_file_content(state["repo_name"], state["filepath"])
    if res["success"]:
        return {"original_code": res["content"], "status_msg": "Code fetched successfully."}
    else:
        return {"status_msg": f"Error fetching code: {res['error']}"}

def code_fixer_node(state: PRState):
    orig_code = state["original_code"]
    issue = state["issue_description"]
    
    prompt = f"""
    You are an Expert Open-Source Contributor.
    Issue/Bug to Fix: {issue}
    
    Original Code:
    {orig_code}
    
    Instructions:
    1. Provide ONLY the complete updated/refactored code cleanly.
    2. Do NOT wrap the code in backticks or markdown explanation blocks.
    """
    response = llm.invoke(prompt)
    clean_code = response.content.replace("```python", "").replace("```markdown", "").replace("```", "").strip()
    
    # Generate PR Title and Summary Description
    meta_prompt = f"Create a concise Pull Request Title and a 2-line PR Description summary for fixing this issue: '{issue}'"
    meta_res = llm.invoke(meta_prompt)
    
    return {
        "fixed_code": clean_code,
        "pr_title": f"fix: {issue[:40]}...",
        "pr_body": meta_res.content
    }

def submit_pr_node(state: PRState):
    result = create_github_pr(
        repo_name=state["repo_name"],
        filepath=state["filepath"],
        new_code=state["fixed_code"],
        pr_title=state["pr_title"],
        pr_body=state["pr_body"]
    )
    return {"status_msg": result}