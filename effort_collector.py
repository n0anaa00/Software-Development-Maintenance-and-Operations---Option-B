import csv
import os
import subprocess
 
def get_loc_by_commit(commit_hash, project_dir):
    """
    Get the total LOC for a specific commit using the scc tool, filtering by programming languages.
 
    Parameters:
    - commit_hash (str): The commit hash to analyze
    - project_dir (str): Path to the project directory
    - languages (list): List of programming languages to include in the analysis
 
    Returns:
    - int: The total LOC for the commit
    """
    # Checkout the commit
    subprocess.run(['git', 'checkout', commit_hash], cwd=project_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # git checkout commit_hash
 
    # Run the scc tool
    result = subprocess.run(['scc', '--no-cocomo', '--no-complexity'], cwd=project_dir, capture_output=True, text=True)
   
    if result.returncode != 0:
        raise RuntimeError(f"scc tool failed: {result.stderr}")
 
    # Parse the LOC data
    loc_total = 0
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 6:
            continue
       
        if parts[0] == "Total":
            loc_total += int(parts[2])
            break
 
    return loc_total
 
def collect_developers_effort(project_dir, output_dir):
    print("Collecting developers' effort...")
    """
    Collect the total count of touched lines of code (TLOCs) for each refactoring and each developer.
 
    Parameters:
    - project_dir (str): Path to the cloned project directory
    - output_dir (str): Path to the output directory for this repository
 
    Output:
    - Saves a CSV file named 'developers-effort.csv' in the output directory
    """
    # TODO: Implement developer effort collection logic
    # 1. Use subprocess to run scc tool
    # 2. Calculate TLOCs for each commit
    # 3. Aggregate data per developer and refactoring type
 
    # Get all commit hashes
    result = subprocess.run(['git', 'log', '--format=%H'], cwd=project_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Git log command failed: {result.stderr}")
 
    commits = result.stdout.splitlines()
 
    effort_data = [["refactoring_hash", "previous_hash", "TLOC"]]
 
    for i in range(1, len(commits)):
        # Count progress:
        print((i / len(commits)) * 100)
        
        refactoring_commit = commits[i]
        previous_commit = commits[i - 1]
 
        try:
            loc_refactoring = get_loc_by_commit(refactoring_commit, project_dir)
            loc_previous = get_loc_by_commit(previous_commit, project_dir)
            tloc = abs(loc_refactoring - loc_previous)
 
            effort_data.append([refactoring_commit, previous_commit, tloc])
        except Exception as e:
            print(f"Error processing commits {refactoring_commit} -> {previous_commit}: {e}")
 
    with open(os.path.join(output_dir, 'developers-effort.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(effort_data) 
