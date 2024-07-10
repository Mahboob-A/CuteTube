import os


curr_dir = os.getcwd()

for root, dirs, files in os.walk(curr_dir):
    print("Root: ", root)
    print("Dirs: ", dirs)
    print("Files: ", files)
