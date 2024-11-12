from pydriller import RepositoryMining
import os
import json

def analyze_diff(repository_path):
    """
    Analyzes the diff changes between each commit and its previous commit in a Git repository.
    
    Args:
        repository_path (str): The local path to the Git repository.

    Returns:
        List[Dict]: A list of dictionaries, each containing information about the diff change per commit.
    """
    diffs = []

    for commit in RepositoryMining(repository_path).traverse_commits():
        commit_info = {
            "hash": commit.hash,
            "author": commit.author.name,
            "date": commit.committer_date,
            "modified_files": []
        }
        
        for modified_file in commit.modifications:
            # Capture file-level changes like lines added and removed
            file_diff = {
                "filename": modified_file.filename,
                "added_lines": modified_file.added_lines,
                "deleted_lines": modified_file.deleted_lines,
                "diff": modified_file.diff  # Optional: Full diff string
            }
            commit_info["modified_files"].append(file_diff)
        
        diffs.append(commit_info)
    
    return diffs

def save_diff_to_file(diffs, output_file):
    """
    Saves the analyzed diff information to a file in JSON format.

    Args:
        diffs (List[Dict]): List of diff information for each commit.
        output_file (str): Path to the output file where results will be saved.
    """
    with open(output_file, 'w') as file:
        json.dump(diffs, file, indent=4, default=str)

# Example implementation:
if __name__ == "__main__":
    repo_path = "path/to/cloned/repository"
    output_path = os.path.join(repo_path, "commit_diffs.json")
    diff_data = analyze_diff(repo_path)
    save_diff_to_file(diff_data, output_path)
    print(f"Diff data saved to {output_path}")
