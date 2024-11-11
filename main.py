from pathlib import Path
import subprocess
import time
from progress.bar import Bar
from progress.spinner import PieSpinner
import json
import re


def mock_upload_file(filepath, remote):
    "Mock function of file upload"
    time.sleep(1)

def upload_file(albums, filepath, remote_name):
    "Real function for uploading"

    # Save image to album.
    album_name: str = filepath.split(r"/")[1]
    if "." in album_name: 
        album_name: str = filepath.split(r"/")[0]
    albums.append(album_name)
    if subprocess.run(["rclone", "copy", filepath, f"{remote_name}:album/'{album_name}'"], capture_output=True).returncode != 0:
        raise FileNotFoundError
    
    return albums

def save_files_list(files_list, savefile):
    "Serialize and save folder structure"
    json.dump(files_list, savefile)

def save_index(index, savefile):
    "Serialize and save progress"
    savefile.seek(0)
    savefile.write(str(index))

def ls_albums(remote):
    "List albums at remote"
    res = subprocess.run(["rclone", "lsd", f"{remote}:album"], capture_output=True)
    if res.returncode != 0:
        raise FileNotFoundError
    return re.findall(r" \d+ (.+)", res.stdout.decode())

class SlowBar(Bar):
    suffix = "at file %(index)d/%(max)d, %(remaining_hours)d hours left "
    @property
    def remaining_hours(self):
        return self.eta // 3600

if __name__ == "__main__":

    remote = "gphotos"

    # ls_albums(remote)
    # exit(0)

    # Folder structure not indexed yet. Do the indexing and save the result.
    if not Path("files.json").exists():

        i = 0
        skipped = []
        dir = input("Enter mass-upload directory: ")
        # dir = "testdir"

        print("Indexing files and sub-files in the given directory.")
        print("Please be patient, it can take a while...")

        try:
            with PieSpinner("Indexing files %(index)d... ") as spinner:
                files = []
                for p in Path(dir).rglob("*"):
                    if Path.is_file: 
                        files.append(str(p))
                    spinner.next()

            with open("files.json", "w") as fp:
                save_files_list(files, fp)

        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            print("Something went wrong, path may not exist.")
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
            try:
                with open("skipped_files.json", "r") as fp:
                    skipped = json.load(fp)
            except:
                skipped = []

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


    # Get a list of existing albums on remote
    albums = ls_albums(remote)


    # Continue uploading files from where it left.
    if i != -1:
        progressfp = open("progress", "w")
        with SlowBar("Uploading", index=i, max=len(files)) as bar:
            while i < len(files):
                filepath = files[i]
                try:
                    albums = upload_file(albums, filepath, remote)
                except FileNotFoundError:
                    print(f"\n\tERROR: Either file is not a media, or it's corrupted. Skipping file: {filepath}...\n")
                    skipped.append(filepath)
                    albums.pop()
                    with open("skipped_files.json", "w") as sf:
                        json.dump(skipped, sf)
                save_index(i, progressfp)
                i += 1
                bar.next()

        i = -1
        progressfp.close()
        save_index(i, progressfp)

    print("Upload completed!")
