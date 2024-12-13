import pandas as pd
import json
import os
from collections import defaultdict

# Step 1: Load multiple CSV files from a directory and detect trivia files
def load_multiple_csv_files(directory_path):
    files_with_dataframes = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            print(f"Loading file: {file_path}")
            # Try reading with different header rows to find 'Status' column
            header_found = False
            for header_row in range(0, 10):  # Try the first 10 rows
                df = pd.read_csv(file_path, header=header_row)
                print(f"Trying header_row={header_row} with columns: {df.columns.tolist()}")
                if 'Status' in df.columns:
                    print(f"'Status' column found with header_row={header_row} in {filename}")
                    header_found = True
                    break
            if not header_found:
                print(f"'Status' column not found in {filename}. Skipping this file.")
                continue  # Skip this file
            # Check if the filename contains "+ trivia" to mark the day as a Trivia Day
            is_trivia_day = '+ trivia' in filename.lower()
            files_with_dataframes.append((df, file_path, is_trivia_day))
    return files_with_dataframes

# Step 2: Extract problem info from filename
def extract_problem_info_from_filename(filename):
    base_name = os.path.basename(filename)
    parts = base_name.split('-')
    problem_number = parts[0].split('_')[0]  # Extract #90 from '#90_SummerBreakCalculus2024'
    problem_label = parts[1].split('_')[0]   # Extract AT07 from 'AT07 + trivia'
    return problem_number, problem_label

# Step 3: Clean the data (remove identifying info, add problem info)
def clean_qualtrics_data(data, filename):
    # Remove unnecessary rows (like "Survey Preview")
    data = data[~((data['Status'] == 'Survey Preview') | (data['DistributionChannel'] == 'preview'))].copy()

    # Remove identifying columns (like GPS, email, etc.)
    identifying_columns = ['LocationLatitude', 'LocationLongitude', 'RecipientLastName',
                           'RecipientFirstName', 'RecipientEmail', 'IPAddress','UserLanguage','Status',
                           'Progress', 'DistributionChannel','Progress','Duration (in seconds)' ,
                           'Finished','ResponseId','L2 confidence','Rethink L2','L1 confidence','L1S confidence','L2 conf after L1',
                           ]
    data.drop(columns=identifying_columns, inplace=True, errors='ignore')

    # Extract Problem Number and Problem Label
    problem_number, problem_label = extract_problem_info_from_filename(filename)
    data['Problem Number'] = problem_number
    data['Problem Label'] = problem_label
    if 'RecordedDate' in data.columns:
        data['RecordedDate'] = pd.to_datetime(data['RecordedDate'], errors='coerce').dt.date

    return data

# Main function to execute the data loading, cleaning, and saving
def main():
    input_directory = "Sample Data"
    output_directory = "Cleaned data"
    os.makedirs(output_directory, exist_ok=True)  # Create output directory if it doesn't exist

    # Load and process each file
    files_with_dataframes = load_multiple_csv_files(input_directory)
    
    for df, file_path, is_trivia_day in files_with_dataframes:
        # Get the filename
        filename = os.path.basename(file_path)
        
        # Clean the data
        cleaned_data = clean_qualtrics_data(df, filename)
        
        # Save cleaned data to output directory
        output_path = os.path.join(output_directory, f"cleaned_{filename}")
        cleaned_data.to_csv(output_path, index=False)
        print(f"Cleaned data saved to: {output_path}")

        # Indicate if it was a trivia day
        if is_trivia_day:
            print(f"{filename} marked as a Trivia Day.")

if __name__ == "__main__":
    main()
