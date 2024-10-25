import csv
import urllib.request
import urllib.error
from pathlib import Path
import sys
from time import sleep

def print_progress(current, total, prefix='Progress:', suffix='Complete', length=50):
    """Simple progress bar"""
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    percent = f"{100 * current / total:.1f}"
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    if current == total:
        print()

def process_github_links(input_file: str, chunk_size: int = 1000) -> None:
    """
    Process CSV file to extract unique project names and convert them to GitHub links.
    
    Args:
        input_file: Path to the input CSV file
        chunk_size: Number of rows to process at a time
    """
    # Initialize sets to store unique successful and failed links
    successful_links = set()
    failed_links = set()
    processed_projects = set()  # To track unique projects we've already seen
    
    # Create output files
    sources_file = Path("sources.txt")
    failed_file = Path("failed.txt")
    
    print("Starting to process the CSV file...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            # Get the index of the 'project' column
            header = next(csv.reader([next(csvfile)]))
            project_idx = header.index('project')
            
            # Reset file pointer to start
            csvfile.seek(0)
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            
            while True:
                # Read chunk_size rows at a time
                chunk = []
                for _ in range(chunk_size):
                    try:
                        row = next(reader)
                        chunk.append(row[project_idx].lower())
                    except StopIteration:
                        break
                
                if not chunk:
                    break
                
                # Process unique projects in this chunk
                unique_projects = set(chunk) - processed_projects
                
                if unique_projects:
                    print(f"\nProcessing {len(unique_projects)} new unique projects...")
                    
                    for i, project in enumerate(unique_projects):
                        # Show progress
                        print_progress(i + 1, len(unique_projects))
                        
                        # Skip if we've already processed this project
                        if project in processed_projects:
                            continue
                        
                        processed_projects.add(project)
                        
                        # Remove 'apache_' prefix if present and create GitHub URL
                        clean_project = project[7:] if project.startswith('apache_') else project
                        github_url = f"https://github.com/apache/{clean_project}"
                        
                        # Test the URL
                        try:
                            # Create a request object with a reasonable timeout
                            req = urllib.request.Request(
                                github_url,
                                method='HEAD',  # Only get headers, not full content
                                headers={'User-Agent': 'Mozilla/5.0'}  # Some servers require this
                            )
                            
                            with urllib.request.urlopen(req, timeout=5) as response:
                                if response.status == 200:
                                    successful_links.add(github_url)
                                else:
                                    failed_links.add(github_url)
                        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
                            failed_links.add(github_url)
                        
                        # Add a small delay to avoid overwhelming the GitHub server
                        sleep(0.1)
                        
                        # Check if we've hit over 50 dead links (probably a bug somewhere)
                        if len(failed_links) > 50:
                            print("\nWarning: More than 50 links have failed! Stopping processing.")
                            raise ValueError("Too many failed links")
                        
                    # Write results after processing each chunk
                    with open(sources_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(sorted(successful_links)) + '\n')
                    
                    with open(failed_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(sorted(failed_links)) + '\n')
                    
                    print(f"\nProgress: {len(successful_links)} successful links, {len(failed_links)} failed links")
    
    except ValueError as e:
        if str(e) == "Too many failed links":
            print("\nProgram stopped due to too many failed links.")
        else:
            print(f"\nAn error occurred: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    
    print("\nFinal results:")
    print(f"Successful links: {len(successful_links)}")
    print(f"Failed links: {len(failed_links)}")
    print(f"Total unique projects processed: {len(processed_projects)}")

if __name__ == "__main__":
    input_file = "sonar_measures.csv"
    process_github_links(input_file)