import pandas as pd
import os
import json

# Badge Functions

def exertion_badge(row):
    l1_answer = str(row.get('L1 problem', '')).lower().strip()
    l2_answer = str(row.get('L2 problem', '')).lower().strip()
    if l1_answer in ['a', 'b', 'c', 'd', 'idk'] and l2_answer in ['a', 'b', 'c', 'd', 'idk']:
        return 'Exertion'
    return None


def endurance_badge(row):
    l1_answer = str(row.get('L1 problem', '')).lower().strip()
    l1s_answer = str(row.get('l1sim problem', '')).lower().strip()
    l2_answer = str(row.get('L2 problem', '')).lower().strip()
    l2s_answer = str(row.get('L2S answer', '')).lower().strip()

    left_star = l1_answer in ['a', 'b', 'c', 'd', 'idk'] and l1s_answer in ['a', 'b', 'c', 'd', 'idk']
    right_star = l2_answer in ['a', 'b', 'c', 'd', 'idk'] and l2s_answer in ['a', 'b', 'c', 'd', 'idk']

    if left_star and right_star:
        return 'Endurance (both stars)'
    elif left_star:
        return 'Endurance (one star - left)'
    elif right_star:
        return 'Endurance (one star - right)'
    return None

def initiative_badge(row):
    starting_level = str(row.get('Starting level', '')).strip()
    l2_answer = str(row.get('L2 problem', '')).lower().strip()
    if starting_level == 'L2 Start' and l2_answer in ['a', 'b', 'c', 'd', 'idk']:
        return 'Initiative'
    return None

def determination_badge(row):
    l1_answer = str(row.get('L1 problem', '')).lower().strip()
    l2_answer = str(row.get('L2 problem', '')).lower().strip()
    l1_hint_answer = str(row.get('L1 answer after hint', '')).lower().strip()
    l2_hint_answer = str(row.get('L2 after hint answer', '')).lower().strip()
    l1s_answer = str(row.get('l1sim problem', '')).lower().strip()
    l2s_answer = str(row.get('L2S answer', '')).lower().strip()
    # l1s_hint_answer = str(row.get('L1S answer after hint', '')).lower().strip()
    # l2s_hint_answer = str(row.get('L2S answer after hint', '')).lower().strip()

    conditions = [
        (l1_answer in ['b', 'c', 'd', 'idk'] and l1_hint_answer in ['a', 'b', 'c', 'd', 'idk']),
        (l1_answer in ['b', 'c', 'd', 'idk'] and l1s_answer in ['a', 'b', 'c', 'd', 'idk']),
        (l2_answer in ['b', 'c', 'd', 'idk'] and l2_hint_answer in ['a', 'b', 'c', 'd', 'idk']),
        (l2_answer in ['b', 'c', 'd', 'idk'] and l2s_answer in ['a', 'b', 'c', 'd', 'idk']),
    ]

    if any(conditions):
        return 'Determination'
    return None

# def commitment_badge(row):
#     # Specify the columns we want to check
#     flashcard_columns = ['L1x1q answer', 'L1x2q answer', 'L2x1q answer', 'L2x2q answer']
    
#     # Count the columns that have non-empty entries
#     star_count = sum(1 for col in flashcard_columns if pd.notnull(row.get(col, '')) and str(row[col]).strip() != '')
    
#     # Return the Community badge with stars if there are any entries
#     if star_count >= 1:
#         return f'Commitment badge ({star_count} star{"s" if star_count > 1 else ""})'
#     return None
def commitment_badge(row):
    # Specify the columns we want to check
    flashcard_columns = ['L1x1q answer', 'L1x2q answer', 'L2x1q answer', 'L2x2q answer']
    
    # Ensure columns exist in the row's index before accessing
    star_count = sum(
        1 for col in flashcard_columns 
        if col in row.index and pd.notnull(row.get(col, '')) and str(row[col]).strip() != ''
    )
    
    # Return the Commitment badge with stars if there are any entries
    if star_count >= 1:
        return f'Commitment badge ({star_count} star{"s" if star_count > 1 else ""})'
    return None



def community_badge(row):
    # Check if the 'Trivia day' column is in the row data
    if 'Trivia Day' not in row:
        return None
    
    # Retrieve the entry from the 'Trivia day' column, if it exists
    trivia_day_entry = str(row.get('Trivia Day', '')).lower().strip()
    # Check for valid entries in the 'Trivia day' column
    if trivia_day_entry in ['calc plus trivia', 'just trivia']:
        return 'Community'
    
    # No badge if the criteria are not met
    return None


# Main function to calculate all badges
def calculate_all_badges(data, trivia_day=False):
    all_badges = []

    for index, row in data.iterrows():
        badges = []

        # Check each badge and add to list if earned
        exertion = exertion_badge(row)
        if exertion:
            badges.append(exertion)

        endurance = endurance_badge(row)
        if endurance:
            badges.append(endurance)

        initiative = initiative_badge(row)
        if initiative:
            badges.append(initiative)

        determination = determination_badge(row)
        if determination:
            badges.append(determination)

        commitment = commitment_badge(row)
        if commitment:
            badges.append(commitment)

        community = community_badge(row)
        if community:
            badges.append(community)

        # Compile results for each student
        student_id = row.get('ExternalReference', 'Unknown')
        all_badges.append({'Student ID': student_id, 'Badges': badges})

        # # Log badge assignment
        # print(f"Student ID: {student_id}, Badges Earned: {badges}")

    return all_badges


def process_file(input_file, output_dir):
    # Load the CSV file into a DataFrame
    data = pd.read_csv(input_file)
    
    # Check if 'Trivia day' column exists
    trivia_day = 'Trivia Day' in data.columns
    
    # Calculate badges
    all_badges = calculate_all_badges(data, trivia_day)
    
    # Prepare output DataFrame
    output_data = pd.DataFrame({
        'Student ID': [entry['Student ID'] for entry in all_badges],
        'Badges': [', '.join(entry['Badges']) for entry in all_badges]
    })
    
    # Remove rows where "Student ID" or "Badges" contains specific unwanted values
    output_data = output_data[
        ~(
            (output_data['Student ID'] == "External Data Reference") | 
            (output_data['Badges'] == "Commitment badge (4 stars)")
        )
    ]
    
    # Generate output filenames based on input file
    base_name = os.path.basename(input_file).replace('cleaned_', 'Badges_cleaned_')
    output_filename_csv = os.path.splitext(base_name)[0] + '.csv'  # CSV filename
    output_filename_json = os.path.splitext(base_name)[0] + '.json'  # JSON filename
    
    # Save the output file as CSV
    output_file_csv = os.path.join(output_dir, output_filename_csv)
    output_data.to_csv(output_file_csv, index=False)

    # Save the output file as JSON
    output_file_json = os.path.join(output_dir, output_filename_json)
    output_data.to_json(output_file_json, orient='records', indent=4)
    
    print(f"Processed {input_file} -> {output_file_csv} and {output_file_json}")


# Main function to process all files in a folder
def process_folder(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Iterate through all CSV files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):  # Process only CSV files
            input_file_path = os.path.join(input_folder, file_name)
            process_file(input_file_path, output_folder)

# Example usage
if __name__ == "__main__":
    # Define input folder and output folder paths
    input_folder = '/Users/udayjagatha/Documents/Badge/badgedocs/Cleaned data'  # Replace with your folder containing cleaned data
    output_folder = 'Badges_data'
    
    # Process all files in the input folder
    process_folder(input_folder, output_folder)