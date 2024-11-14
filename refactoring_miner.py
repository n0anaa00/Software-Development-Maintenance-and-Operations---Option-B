import csv
import json
import os
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED


miner_dir = os.path.join("RefactoringMiner-3.0.9", "bin", "RefactoringMiner")


def mine_refactoring_activity(project_dir, output_dir):

    # Setting up the refactoring data
    refactoring_data = {"Total Refactorings":0, "Average Number of Commits Between Refactorings":0, "Average Refactors per Refactoring Commit":0}
    commits_all = 0
    commits_refactoring = 0
    

    # Setting up the output file path variables
    json_output = os.path.join(output_dir, "rminer_output.json")
    csv_output = os.path.join(output_dir, "rminer_analysis.csv")
    zip_output = os.path.join(output_dir, "rminer_output.zip")
    
    
    # Mining the repository
    try:
        print(f"Mining {project_dir}")
        if os.name == 'nt':  # Windows, attempting to guarantee the code working
            subprocess.run(["RefactoringMiner", "-a", project_dir, "-json", json_output], shell=True)
        else: # Linux
            subprocess.run([miner_dir, "-a", project_dir, "-json", json_output])
    except subprocess.CalledProcessError as e:
        print(f"Error while mining {e}")
        raise
    

    # Collecting statistics from the data
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
    
    refactoring_data['Average Number of Commits Between Refactorings'] = commits_all / commits_refactoring
    refactoring_data['Average Refactors per Refactoring Commit'] = refactoring_data['Total Refactorings'] / commits_refactoring


    # Saving the statistics to a .csv file
    with open(csv_output, 'w', newline='') as output:
        csvwriter = csv.writer(output)

        for key in refactoring_data:
            csvwriter.writerow([key, refactoring_data[key]])


    # Compressing the RMiner output .json and deleting the .json to save space
    with ZipFile(zip_output, 'w', ZIP_DEFLATED, compresslevel=9) as zip:
        zip.write(json_output, "rminer_output.json")

    if os.path.exists(json_output):
        os.remove(json_output)
    else:
        print(f"{json_output} does not exist, could not delete the file.")




if __name__ == "__main__":
    # Code for testing purposes
    project = os.path.join("repository")
    output = os.path.join("Outputs", "ant")
    mine_refactoring_activity(project, output)