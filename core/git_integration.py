# core/git_integration.py
from git import Repo
import os

class GitIntegration:
    def __init__(self):
        self.repo = None

    def clone_repo(self, url: str, target_dir: str) -> bool:
        """Clones a repo from a URL."""
        try:
            self.repo = Repo.clone_from(url, target_dir)
            return True
        except Exception as e:
            print(f"Clone failed: {e}")
            return False

    def get_commit_history(self, file_path: str, max_commits=5) -> str:
        """Gets commit history for a file."""
        if not self.repo:
            return "No repo loaded."
        try:
            commits = list(self.repo.iter_commits(paths=file_path, max_count=max_commits))
            history = "\n".join([f"{c.hexsha[:8]} - {c.message.strip()} ({c.authored_datetime})" for c in commits])
            return history if history else "No commits found."
        except Exception as e:
            return f"Error fetching history: {e}"