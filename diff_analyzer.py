from pydriller.repository import Repository
import os
import json
import requests

def calculate_and_collect_diff(repository_path, output_file, repo_type="github", jira_base_url=None, project_key=None, auth_token=None):
    """
    Analyzes the diff changes between each commit and its previous commit in a Git or Jira repository,
    and saves the output to a JSON file.

    Args:
        repository_path (str): The local path to the Git repository.
        output_file (str): Path to the output file where results will be saved.
        repo_type (str): The type of repository, either 'github' or 'jira'.
        jira_base_url (str, optional): Base URL of the Jira instance (required for Jira repos).
        project_key (str, optional): Key of the Jira project (required for Jira repos).
        auth_token (str, optional): Authentication token for Jira API (required for Jira repos).
    """
    diffs = []

    if repo_type.lower() == "github":
        # Use pydriller for GitHub repositories
        for commit in Repository(repository_path).traverse_commits():
            commit_info = {
                "hash": commit.hash,
                "author": commit.author.name,
                "date": commit.committer_date,
                "modified_files": []
            }
            
            for modified_file in commit.modified_files:
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

                diffs.append(issue_data)
        else:
            print("Failed to fetch issues from Jira:", response.status_code, response.text)

    # Save the collected diffs to the specified output file
    with open(output_file, 'w') as file:
        json.dump(diffs, file, indent=4, default=str)
    print(f"Diff data saved to {output_file}")

