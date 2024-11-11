from pathlib import Path
import subprocess
import time
from progress.bar import Bar
import json


def mock_upload_file(filepath, remote):
    "Mock function of file upload"
    time.sleep(1)

def upload_file(filepath, remote_name):
    "Real function for uploading"
    if subprocess.run(["rclone", "copy", filepath, f"{remote_name}:upload"], capture_output=True).returncode != 0:
        raise Exception

def save_files_list(files_list, savefile):
    "Serialize and save folder structure"
    json.dump(files_list, savefile)

def save_index(index, savefile):
    "Serialize and save progress"
    savefile.seek(0)
    savefile.write(str(index))


if __name__ == "__main__":

    remote = "gphotos"

    # Folder structure not indexed yet. Do the indexing and save the result.
    if not Path("files.json").exists():

        i = 0
        # dir = input("Enter mass-upload directory: ")
        dir = "testdir"
        try:
            files = list(str(p) for p in Path(dir).rglob("*") if Path.is_file(p))
            with open("files.json", "w") as fp:
                save_files_list(files, fp)
        except:
            print("Something went wrong...")
            exit(1)

    # Indexing done, load indexing.
    else:

        with open("files.json", "r") as fp:
            files = json.load(fp)

        # No progress (index) file. Start from 0.
        if not Path("progress").exists():
            i = 0
            print(i)

        # Create a new progress file.
        else:
            with open("progress") as p:
                i = int("".join(p.readline()))
                print(i)
    
    # Continue uploading files from where it left.
    print(i)
    if i != -1:
        progressfp = open("progress", "w")
        with Bar("Uploading", index=i, max=len(files), suffix = f"at file %(index)d") as bar:
            while i < len(files):
                filepath = files[i]
                try:
                    upload_file(filepath, remote)
                except:
                    print(f"\n\tERROR: Either file is not a media, or it's corrupted. Skipping file: {filepath}...\n")
                save_index(i, progressfp)
                i += 1
                bar.next()

        i = -1
        save_index(i, progressfp)

    print("Upload completed!")
