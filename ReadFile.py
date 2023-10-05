import subprocess

# four files
file_names = [
    "epl_ratings_20182019",
    "epl_matches_20152016",
    "epl_matches_20162017",
    "epl_matches_20172018"
]

# read files
file_contents = {}
for file_name in file_names:
    with open(file_name, 'r') as file:
        file_contents[file_name] = file.read()

# In this part: Put Data into PAT 3



# Start PAT3

result = subprocess.run(['PAT 3', '12115_away.pcsp'], capture_output=True, text=True)

# Output from PAT3
print(result.stdout)

if result.returncode != 0:
    print("Error:", result.stderr)
