import os
import json

def ensure_and_clear_file(file_path):
    """
    Ensure the file exists and clear its contents.
    
    :param file_path: Path to the file to be cleared/created
    """
    # Open the file in write mode (creates it if it doesn't exist, clears it if it does)
    with open(file_path, 'w') as f:
        pass

def check_repo_files(base_path):
    """
    Check for missing files in Apache repo output folders and create txt files 
    with GitHub links for missing files.
    
    :param base_path: Path to the base directory containing 'Outputs' folder
    """
    # Paths to output files
    no_diff_path = os.path.join(base_path, 'no_diff.txt')
    no_effort_path = os.path.join(base_path, 'no_effort.txt')
    no_bugfix_path = os.path.join(base_path, 'no_bugfix.txt')
    
    # Ensure files exist and are cleared
    ensure_and_clear_file(no_diff_path)
    ensure_and_clear_file(no_effort_path)
    ensure_and_clear_file(no_bugfix_path)
    
    # Output files to track missing files
    no_diff_repos = []
    no_effort_repos = []
    no_bugfix_repos = []
    
    # Path to Outputs folder
    outputs_path = os.path.join(base_path, 'Outputs')
    
    # Iterate through all subdirectories in Outputs
    for repo_folder in os.listdir(outputs_path):
        repo_path = os.path.join(outputs_path, repo_folder)
        
        # Skip if not a directory
        if not os.path.isdir(repo_path):
            continue
        
        # Check for specific files
        diff_path = os.path.join(repo_path, 'diff_analysis.json')
        effort_path = os.path.join(repo_path, 'developers-effort.csv')
        bugfix_path = os.path.join(repo_path, repo_folder, 'bug-fixing-commits.json')
        
        # Check and record missing files
        if not os.path.exists(diff_path):
            no_diff_repos.append(f"https://github.com/apache/{repo_folder}")
        
        if not os.path.exists(effort_path):
            no_effort_repos.append(f"https://github.com/apache/{repo_folder}")
        
        if not os.path.exists(bugfix_path):
            no_bugfix_repos.append(f"https://github.com/apache/{repo_folder}")
    
    # Write results to files
    def write_links_to_file(file_path, repos):
        with open(file_path, 'w') as f:
            for repo in sorted(repos):
                f.write(f"{repo}\n")
    
    write_links_to_file(no_diff_path, no_diff_repos)
    write_links_to_file(no_effort_path, no_effort_repos)
    write_links_to_file(no_bugfix_path, no_bugfix_repos)
    
    # Print summary
    print(f"Repos missing diff_analysis.json: {len(no_diff_repos)}")
    print(f"Repos missing developers-effort.csv: {len(no_effort_repos)}")
    print(f"Repos missing bug-fixing-commits.json: {len(no_bugfix_repos)}")

def main():
    # Get the directory of the script
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Run the file checking function
    check_repo_files(base_path)

if __name__ == "__main__":
    main()