from pydriller import RepositoryMining
import os
import json
import requests

def calculate_and_collect_diff(repository_path, repo_type="github", jira_base_url=None, project_key=None, auth_token=None):
    """
    Analyzes the diff changes between each commit and its previous commit in a Git or Jira repository.
    
    Args:
        repository_path (str): The local path to the Git repository.
        repo_type (str): The type of repository, either 'github' or 'jira'.
        jira_base_url (str, optional): Base URL of the Jira instance (required for Jira repos).
        project_key (str, optional): Key of the Jira project (required for Jira repos).
        auth_token (str, optional): Authentication token for Jira API (required for Jira repos).

    Returns:
        List[Dict]: A list of dictionaries, each containing information about the diff change per commit or issue.
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

    elif repo_type.lower() == "jira" and jira_base_url and project_key and auth_token:
        # For Jira repositories, retrieve issue data with Jira API
        diffs = fetch_jira_issues(jira_base_url, project_key, auth_token)

    return diffs

def fetch_jira_issues(jira_base_url, project_key, auth_token):
    """
    Fetches issues from a Jira repository and calculates diff change between issue statuses.
    
    Args:
        jira_base_url (str): Base URL of the Jira instance.
        project_key (str): Key of the Jira project.
        auth_token (str): Authentication token for Jira API.

    Returns:
        List[Dict]: List of issue data with change history from Jira.
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
                "updated": issue["fields"]["updated"],
                "changelog": []  # to store diff-like changes in the issue history
            }
            # Add change history for each issue
            changelog_url = f"{jira_base_url}/rest/api/2/issue/{issue['key']}/changelog"
            changelog_response = requests.get(changelog_url, headers=headers)
            if changelog_response.status_code == 200:
                changelogs = changelog_response.json().get("values", [])
                for change in changelogs:
                    change_data = {
                        "author": change["author"]["displayName"],
                        "date": change["created"],
                        "items": []
                    }
                    for item in change["items"]:
                        # Track status changes or other field modifications
                        if item["field"] == "status":
                            item_data = {
                                "field": item["field"],
                                "from": item["fromString"],
                                "to": item["toString"]
                            }
                            change_data["items"].append(item_data)
                    issue_data["changelog"].append(change_data)

            jira_issues.append(issue_data)
    else:
        print("Failed to fetch Jira issues:", response.status_code, response.text)
    
    return jira_issues

def save_diff_to_file(diffs, output_file):
    """
    Saves the analyzed diff information to a file in JSON format.

    Args:
        diffs (List[Dict]): List of diff information for each commit or issue.
        output_file (str): Path to the output file where results will be saved.
    """
    with open(output_file, 'w') as file:
        json.dump(diffs, file, indent=4, default=str)



    save_diff_to_file(diff_data, output_path)
    print(f"Diff data saved to {output_path}")