import os
import json
from collections import defaultdict

# Specify the directory containing the JSON files
directory_path = "/Users/udayjagatha/Documents/Badge/badgedocs/Badges_data"

# Output file path
output_file_path = "totalbadgecount.json"

# Dictionary to store badge counts
student_badge_counts = defaultdict(lambda: defaultdict(int))
overall_badge_counts = defaultdict(int)

# Loop through all JSON files in the directory
try:
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):  # Only process JSON files
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                for record in data:
                    student_id = record["Student ID"]
                    badges = record["Badges"]
                    if badges:  # Only process if there are badges
                        for badge in map(str.strip, badges.split(',')):
                            student_badge_counts[student_id][badge] += 1
                            overall_badge_counts[badge] += 1
except FileNotFoundError as e:
    print(f"Directory not found: {e}")
    exit()

# Prepare the output structure
output_data = {
    "BadgeCountsByStudent": {
        student: dict(badges) for student, badges in student_badge_counts.items()
    },
    "OverallBadgeCounts": dict(overall_badge_counts)
}

# Write the output to a JSON file
try:
    with open(output_file_path, 'w') as output_file:
        json.dump(output_data, output_file, indent=4)
    print(f"Output saved to {output_file_path}")
except Exception as e:
    print(f"Error writing to output file: {e}")
