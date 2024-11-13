import json
import os
import requests
from time import sleep

# GitHub and Jira API URLs
jira_projects_url = "https://issues.apache.org/jira/rest/api/2/project"
jira_issues_url = "https://issues.apache.org/jira/rest/api/2/search"


def mine_bug_fixing_commits_api(project_url, output_dir, github_token):
    """
    Attempt to mine bug-fixing commits from GitHub. If issues are not found, fall back to Jira.
    """
    print(f"Mining bug-fixing commits for {project_url} via GitHub API...")

    # Extract owner and repo name from project URL
    owner_repo = project_url.rstrip('/').split('/')[-2:]
    repo_owner, repo_name = owner_repo[0], owner_repo[1]

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # GitHub Issues
    issues_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    response = requests.get(issues_url, headers=headers, params={"state": "all"})
    
    if response.status_code == 200 and response.json():
        issues = response.json()
        bug_fixing_commits = fetch_commits_from_github(repo_owner, repo_name, headers, issues)
        save_bug_data(output_dir, repo_name, True, bug_fixing_commits, issues)
    else:
        print(f"No GitHub issues found for {repo_name}. Attempting to fetch Jira issues.")
        fetch_issues_from_jira(output_dir)


def fetch_commits_from_github(repo_owner, repo_name, headers, issues):
    """
    Helper function to fetch commits from GitHub based on keywords.
    """
    commits_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    response = requests.get(commits_url, headers=headers)
    commits = response.json()
    bug_fixing_commits = []

    for commit in commits:
        commit_message = commit['commit']['message'].lower()
        if "fix" in commit_message or "bug" in commit_message or "error" in commit_message:
            associated_issue = next((issue['number'] for issue in issues if f"#{issue['number']}" in commit_message), None)
            bug_fixing_commits.append({
                "commit_hash": commit['sha'],
                "commit_message": commit['commit']['message'],
                "associated_issue": associated_issue
            })
    
    return bug_fixing_commits


def fetch_issues_from_jira(project_file, output_dir):
    """
    Fetch all bug-fixing issues from Jira for each project listed in the provided file.
    
    Parameters:
    - project_file (str): Path to the text file containing GitHub project URLs.
    - output_dir (str): Directory where JSON files with issue data will be saved.
    """
    # Read all project URLs from the file
    with open(project_file, 'r') as f:
        project_urls = [line.strip() for line in f if line.strip()]

    for project_url in project_urls:
        # Extract the project key (last part of the URL)
        project_key = project_url.rstrip('/').split('/')[-1]
        print(f"Processing project: {project_key}")

        # Set up directory and file paths for each project
        project_folder = os.path.join(output_dir, project_key)
        os.makedirs(project_folder, exist_ok=True)
        output_file = os.path.join(project_folder, "bug_fixes.json")

        project_data = {"using_github_issues": False, "bug_fixing_commits": [], "issue_data": []}
        start_at = 0
        page_size = 50  # Define page size for Jira API pagination

        while True:
            # Set up parameters for the paginated issue search
            params = {
                "jql": f"project = '{project_key}' AND issuetype = Bug AND status in (Closed, Resolved)",
                "startAt": start_at,
                "maxResults": page_size
            }

            response = requests.get(jira_issues_url, params=params)
            if response.status_code == 200:
                issues = response.json().get("issues", [])
                for issue in issues:
                    issue_data = {
                        "project_key": project_key,
                        "issue_number": issue["id"],
                        "title": issue["fields"]["summary"],
                        "body": issue["fields"].get("description", ""),
                        "state": issue["fields"]["status"]["name"].lower()
                    }
                    project_data["issue_data"].append(issue_data)

                # Update start_at for the next page
                start_at += page_size

                # Exit loop if no more issues are available
                if len(issues) < page_size:
                    break
            else:
                print(f"Failed to retrieve issues for project {project_key}. Status code: {response.status_code}")
                break

            # Write the project data to a JSON file
            with open(output_file, "w") as f:
                json.dump(project_data, f, indent=4)
            print(f"Jira data for project {project_key} written to {output_file}")

    else:
        print(f"Failed to retrieve Jira projects. Status code: {response.status_code}")



def save_bug_data(output_dir, repo_name, using_github_issues, bug_fixing_commits, issues):
    """
    Save bug-fixing commit and issue data to a JSON file.
    """
    project_output_dir = os.path.join(output_dir, repo_name)
    os.makedirs(project_output_dir, exist_ok=True)
    output_file = os.path.join(project_output_dir, 'bug-fixing-commits.json')
    issue_data = [
        {
            "issue_number": issue['number'],
            "title": issue['title'],
            "body": issue['body'],
            "state": issue['state']
        }
        for issue in issues
    ]

    bug_data = {
        "using_github_issues": using_github_issues,
        "bug_fixing_commits": bug_fixing_commits,
        "issue_data": issue_data
    }

    with open(output_file, 'w') as f:
        json.dump(bug_data, f, indent=2)
    print(f"Bug-fixing data saved to {output_file}")


def mine_multiple_projects_from_file(sources_file, output_dir, github_token):
    """
    Mine bug-fixing commits for multiple projects using GitHub, falling back to Jira if needed.
    """
    with open(sources_file, 'r') as f:
        project_urls = [line.strip() for line in f if line.strip()]

    for url in project_urls:
        try:
            mine_bug_fixing_commits_api(url, output_dir, github_token)
            sleep(0.5)  # Respect GitHub API rate limits
        except Exception as exc:
            print(f"Failed processing {url} due to {exc}")


# Example usage:
sources_file = "sources.txt"
output_dir = "Outputs"
github_token = "" # APPLY TOKEN HERE
mine_multiple_projects_from_file(sources_file, output_dir, github_token)
