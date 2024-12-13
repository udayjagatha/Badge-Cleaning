import pandas as pd
import os
import re
import json

def extract_problem_number(file_name):
    """
    Extract the problem number after the character '#' in the file name.
    """
    match = re.search(r'#(\d+)', file_name)
    return int(match.group(1)) if match else None

def calculate_streaks(folder_path, output_file):
    """
    Calculate the current streak for all students across multiple files and save results as JSON.

    Args:
        folder_path (str): Path to the folder containing input files.
        output_file (str): Path to save the streak results.
    """
    # List all CSV files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    # Extract problem numbers and sort files by them
    files_with_numbers = [(file, extract_problem_number(file)) for file in files]
    sorted_files = sorted(files_with_numbers, key=lambda x: x[1])
    
    # Initialize streak counters for students
    streaks = {}
    
    # Process files in sorted order
    previous_problem_number = None
    for file, problem_number in sorted_files:
        # Load the current file into a DataFrame
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)
        
        # Ensure the RecordedDate column is in datetime format
        if 'RecordedDate' not in data.columns or 'ExternalReference' not in data.columns:
            print(f"Skipping file {file}: Missing 'RecordedDate' or 'ExternalReference' column.")
            continue
        data['RecordedDate'] = pd.to_datetime(data['RecordedDate'])
        
        # Check if the current file is consecutive to the previous one
        if previous_problem_number is not None and problem_number != previous_problem_number + 1:
            # If not consecutive, reset streaks for all students
            for student in streaks:
                streaks[student] = 0
        
        # Get the list of students in the current file
        current_students = set(data['ExternalReference'].dropna().unique())
        
        # Update streaks
        for student in streaks:
            if student in current_students:
                # Increment streak if the student is present
                streaks[student] += 1
            else:
                # Reset streak if the student is missing
                streaks[student] = 0
        
        # Add new students from the current file
        for student in current_students:
            if student not in streaks:
                streaks[student] = 1
        
        # Update the previous problem number
        previous_problem_number = problem_number
    
    # Convert streaks to JSON format
    streak_data = [{'Student ID': student, 'Current Streak': streak} for student, streak in streaks.items()]
    
    # Save the streak data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(streak_data, json_file, indent=4)
    
    print(f"Streak results saved to {output_file}")

# Example usage
if __name__ == "__main__":
    folder_path = "Cleaned data"  # Replace with the folder containing your files
    output_file = "streak_results.json"
    calculate_streaks(folder_path, output_file)
