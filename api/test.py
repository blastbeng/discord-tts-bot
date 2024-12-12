import os
file_path = os.path.abspath(os.curdir) + "/config/voices_it.json"

with open(file_path, 'r') as f:
    print(f.read())