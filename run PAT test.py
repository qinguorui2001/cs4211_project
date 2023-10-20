import subprocess

consolePath = 'C:\\Program Files\\Process Analysis Toolkit\\Process Analysis Toolkit 3.5.1\\PAT3.Console.exe'
# Define the command to run
#command = [consolePath, '-pcsp', '-d', 'C:\\Users\\nicky\\Desktop\\pcspDir', 'C:\\Users\\nicky\\Desktop\\pcspDir\\output.txt']
#command = [consolePath, '-pcsp', '-d', 'C:\\Users\\nicky\\Desktop\\pcspDir', 'C:\\Users\\nicky\\Desktop\\pcspDir\\output.txt']

import os

# Define the directory path
dir_path = 'C:\\Users\\nicky\\Desktop\\pcspDir'

# Get a list of all files in the directory
file_list = os.listdir(dir_path)

# Iterate over the list and read each file
ind = 0
for file_name in file_list:
    file_path = os.path.join(dir_path, file_name)
    file_out = f"C:\\Users\\nicky\\Desktop\\pcspDir\\output{ind}.txt" #Should not be in same directory as pcsp since it might interfere with the for loop
    if not os.path.isfile(file_out):
        # Create destination file if it does not exist
        open(file_out, 'w').close()
    command = [consolePath, '-pcsp',file_path, file_out]
    result = subprocess.check_output(command)
    print(result)
    ind = ind + 1
        