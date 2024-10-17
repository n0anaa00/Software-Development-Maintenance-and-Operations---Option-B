import json
from pydriller import RepositoryMining
import os






def calculate_and_collect_diff(project_dir, output_dir):
    print("Calculating and collecting diff changes...")
    """
    Calculate and collect the diff changes between detected commits and their previous commits.

    Parameters:
    - project_dir (str): Path to the cloned project directory
    - output_dir (str): Path to the output directory for this repository

    Output:
    - Saves a JSON file named 'commit-diffs.json' in the output directory
    """
    # TODO: Implement diff analysis logic using pydriller

    # Placeholder output
    diff_data = [
        {
            "commit_hash": "abc123",
            "previous_commit_hash": "def456",
            "diff_stats": {
                "files_changed": 3,
                "insertions": 10,
                "deletions": 5
            },
            "diff_content": "Sample diff content"
        }
    ]

     
    for commit in RepositoryMining(project_dir).traverse_commits():
        commit_info = {
            "commit_hash": commit.hash,
            "previous_commit_hash": commit.parents[0].hash if commit.parents else None,
            "diff_stats": {
                "files_changed": len(commit.modified_files),
                "insertions": sum(file.added for file in commit.modified_files),
                "deletions": sum(file.deleted for file in commit.modified_files)
            },
            "diff_content": ""
        }



    for modified_file in commit.modified_files:
            commit_info["diff_content"] += f"--- {modified_file.filename}\n"
            commit_info["diff_content"] += f"+++ {modified_file.filename}\n"
            commit_info["diff_content"] += modified_file.diff + "\n"

        diff_data.append(commit_info)
        
    
    print(f"Diff changes collected and saved to {os.path.join(output_dir, 'commit-diffs.json')}.")



    with open(os.path.join(output_dir, 'commit-diffs.json'), 'w') as f:
        json.dump(diff_data, f, indent=2)

