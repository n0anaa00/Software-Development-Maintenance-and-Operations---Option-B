import csv
import json
import os
import subprocess


miner_dir = os.path.join("RefactoringMiner-3.0.9", "bin", "RefactoringMiner")


def mine_refactoring_activity(project_dir, output_dir):
    refactoring_data = {"Total Refactorings":0,"Time Between Refactorings":0, "Average Refactors per Refactoring Commit":0}
    commits_all = 0
    commits_refactoring = 0
    json_output = os.path.join(output_dir, "rminer_output.json")
    csv_output = os.path.join(output_dir, "rminer_analysis.csv")
    
    try:
        print(f"Mining {project_dir}")
        subprocess.run([miner_dir, "-a", project_dir, "-json", json_output])
    except subprocess.CalledProcessError as e:
        print(f"Error while mining {e}")
        raise
    
    with open(json_output, 'r') as json_data:
        miner_output = json.load(json_data)
    
    for commit in miner_output['commits']:
        commits_all += 1
        if commit['refactorings']:
            commits_refactoring += 1
            for refactor in commit['refactorings']:
                if refactor['type'] not in refactoring_data:
                    refactoring_data[refactor['type']] = 1
                else:
                    refactoring_data[refactor['type']] += 1
                refactoring_data['Total Refactorings'] += 1
    
    print(commits_all)
    print(commits_refactoring)
    refactoring_data['Time Between Refactorings'] = commits_all / commits_refactoring
    refactoring_data['Average Refactors per Refactoring Commit'] = refactoring_data['Total Refactorings'] / commits_refactoring

    with open(csv_output, 'w', newline='') as output:
        csvwriter = csv.writer(output)

        for key in refactoring_data:
            csvwriter.writerow([key, refactoring_data[key]])


    """
    Mine the refactoring activity applied in the history of the cloned projects.

    Parameters:
    - project_dir (str): Path to the cloned project directory
    - output_dir (str): Path to the output directory for this repository

    Output:
    - Saves a JSON file named 'rminer-output.json' in the output directory
    
    # TODO: Implement RefactoringMiner logic
    # 1. Build and run RefactoringMiner tool
    # 2. Parse the output
    # 3. Calculate statistics

    # Placeholder output
    refactoring_data = {
        "total_refactorings": {
            "refactoring_type_1": 10,
            "refactoring_type_2": 5,
        },
        "avg_inter_refactoring_period": 3.5
    }
"""

if __name__ == "__main__":
    project = os.path.join("repository")
    output = os.path.join("Outputs", "ant")
    mine_refactoring_activity(project, output)