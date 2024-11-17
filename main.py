
import time
import os
import shutil
import json
import csv
import subprocess
from refactoring_miner import mine_refactoring_activity
from diff_analyzer import calculate_and_collect_diff
from effort_collector import collect_developers_effort
from bug_miner import mine_bug_fixing_commits_api

def clone_repository(repo_url, target_dir):
    print(f"Cloning repository: {repo_url}")
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True, text=True)
        print(f"Successfully cloned repository to {target_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        print(f"Git output: {e.output}")
        raise

def delete_repository(repo_dir):
    if os.name == 'nt':  # Windows
        os.system(f'rmdir /S /Q "{repo_dir}"')
    else:  # Linux and other Unix-like systems
        os.system(f'rm -rf "{repo_dir}"')
    print(f"Successfully deleted {repo_dir}")

def create_output_directory(repo_name):
    output_dir = os.path.join("Outputs", repo_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    # Read GitHub project URLs from a file
    with open('sources.txt', 'r') as f:
        project_urls = f.read().splitlines()

    for project_url in project_urls:
        repo_name = os.path.basename(project_url).replace('.git', '')
        project_dir = os.path.join("Repos", repo_name)
        output_dir = create_output_directory(repo_name)

        try:
            # Clone the repository
            clone_repository(project_url, project_dir)

            # Perform analysis tasks
            #mine_refactoring_activity(project_dir, output_dir)
            calculate_and_collect_diff(project_dir, output_dir)
            collect_developers_effort(project_dir, output_dir)
            mine_bug_fixing_commits_api(project_url, output_dir)

        except Exception as e:
            print(f"An error occurred while processing {repo_name}: {str(e)}")

        finally:
            time.sleep(2)
            # Delete the repository to save space
            if os.path.exists(project_dir):
                delete_repository(project_dir)

if __name__ == "__main__":
    main()

