from pydriller import RepositoryMining
import os
import json
import requests

def calculate_and_collect_diff(repository_path, repo_type="github"):
    """
    Analyzes the diff changes between each commit and its previous commit in a Git repository.

    Args:
        repository_path (str): The local path to the Git repository.
        repo_type (str): Type of repository, either 'github' or 'jira'.

    Returns:
        List[Dict]: A list of dictionaries, each containing information about the diff change per commit.
    """
    diffs = []

    if repo_type.lower() == "github":
        # Use pydriller for GitHub repositories
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

    elif repo_type.lower() == "jira":
        # For Jira repositories, handle the Jira API logic
        diffs = fetch_jira_issues(repository_path)  # Placeholder for Jira API integration
    
    return diffs

def fetch_jira_issues(jira_base_url, project_key, auth_token):
    """
    Fetches issues from a Jira repository using the Jira REST API.

    Args:
        jira_base_url (str): Base URL of the Jira instance.
        project_key (str): Key of the Jira project.
        auth_token (str): Authentication token for Jira API.

    Returns:
        List[Dict]: List of issue data fetched from Jira.
    """
    jira_issues = []
    url = f"{jira_base_url}/rest/api/2/search"
    headers = {"Authorization": f"Bearer {auth_token}"}
    params = {"jql": f"project={project_key}", "maxResults": 1000}  # Adjust as needed

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        issues = response.json().get("issues", [])
        for issue in issues:
            issue_data = {
                "key": issue["key"],
                "summary": issue["fields"]["summary"],
                "status": issue["fields"]["status"]["name"],
                "created": issue["fields"]["created"],
                "updated": issue["fields"]["updated"]
            }
            jira_issues.append(issue_data)
    else:
        print("Failed to fetch Jira issues:", response.status_code, response.text)
    
    return jira_issues

def save_diff_to_file(diffs, output_file):
    """
    Saves the analyzed diff information to a file in JSON format.

    Args:
        diffs (List[Dict]): List of diff information for each commit.
        output_file (str): Path to the output file where results will be saved.
    """
    with open(output_file, 'w') as file:
        json.dump(diffs, file, indent=4, default=str)

# Example usage:
if __name__ == "__main__":
    repo_path = "path/to/cloned/repository"
    output_path = os.path.join(repo_path, "commit_diffs.json")
    
    # Specify the repo type (github or jira)
    repo_type = "github"  # Change to "jira" if you are working with a Jira repository

    if repo_type == "jira":
        # Jira-specific settings
        jira_base_url = "https://your-jira-instance.atlassian.net"
        project_key = "YOUR_PROJECT_KEY"
        auth_token = "YOUR_JIRA_AUTH_TOKEN"  # You may use API tokens
        diff_data = fetch_jira_issues(jira_base_url, project_key, auth_token)
    else:
        diff_data = calculate_and_collect_diff(repo_path, repo_type)
    
    save_diff_to_file(diff_data, output_path)
    print(f"Diff data saved to {output_path}")