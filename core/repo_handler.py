import os
import git
import tempfile

def clone_repository(url):
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(url, temp_dir)
    return temp_dir

def get_folder_contents(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder)]