import os
import time
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_repo_file_content(repo_name: str, filepath: str) -> dict:
    """Fetches original code from the target GitHub Repository."""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(filepath)
        return {
            "success": True, 
            "content": contents.decoded_content.decode("utf-8"), 
            "sha": contents.sha
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_github_pr(repo_name: str, filepath: str, new_code: str, pr_title: str, pr_body: str) -> str:
    """Creates a new branch on GitHub, commits the fix, and opens a real Pull Request!"""
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(repo_name)
        
        # 1. Get default branch (e.g., main or master)
        default_branch = repo.default_branch
        main_ref = repo.get_git_ref(f"heads/{default_branch}")
        
        # 2. Create a unique new branch for our AI fix
        new_branch_name = f"ai-fix-{int(time.time())}"
        repo.create_git_ref(f"refs/heads/{new_branch_name}", main_ref.object.sha)
        
        # 3. Get existing file SHA reference
        file_obj = repo.get_contents(filepath, ref=default_branch)
        
        # 4. Commit updated code to the new branch
        repo.update_file(
            path=filepath,
            message=pr_title,
            content=new_code,
            sha=file_obj.sha,
            branch=new_branch_name
        )
        
        # 5. Open Official Pull Request
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=new_branch_name,
            base=default_branch
        )
        
        return f"🎉 PULL REQUEST CREATED SUCCESSFULLY!\n\n🔗 **PR Link:** {pr.html_url}"
    except Exception as e:
        return f"❌ Failed to create PR: {str(e)}"