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
        raise FileNotFoundError

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
        skipped = []
        dir = input("Enter mass-upload directory: ")
        # dir = "testdir"
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

        # No info about skipped files.
        if not Path("skipped_files.json").exists():
            skipped = []
        
        # There exist info.
        else:
            with open("skipped_files.json", "r") as fp:
                skipped = json.load(fp)

        # No progress (index) file. Start from 0.
        if not Path("progress").exists():
            i = 0
            skipped = []

        # Read index from progress file.
        else:
            with open("progress") as p:
                try:
                    i = int("".join(p.readline()))
                except ValueError:
                    i = 0

        # If progress (index) is 0, remove skipped_files.json
        if i == 0:
            with open("skipped_files.json", "w") as fp:
                skipped = []

    # Continue uploading files from where it left.
    if i != -1:
        progressfp = open("progress", "w")
        with Bar("Uploading", index=i, max=len(files), suffix = "at file %(index)d/%(max)d") as bar:
            while i < len(files):
                filepath = files[i]
                try:
                    upload_file(filepath, remote)
                except FileNotFoundError:
                    print(f"\n\tERROR: Either file is not a media, or it's corrupted. Skipping file: {filepath}...\n")
                    skipped.append(filepath)
                    with open("skipped_files.json", "w") as sf:
                        json.dump(skipped, sf)
                save_index(i, progressfp)
                i += 1
                bar.next()

        i = -1
        progressfp.close()
        save_index(i, progressfp)

    print("Upload completed!")
