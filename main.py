from pathlib import Path
import time
import json


def upload_file(filepath):
    "Mock function of file upload"
    time.sleep(1)
    print(f"{filepath} uploaded successfully!")


def save_files_list(files_list, savefile):
    "Serialize and save folder structure"
    json.dump(files_list, savefile)


def save_index(index, savefile):
    "Serialize and save progress"
    savefile.seek(0)
    savefile.write(str(index))



if __name__ == "__main__":

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

        # Create a new progress file.
        else:
            with open("progress") as p:
                i = int(p.read(1))
            progressfp = open("progress", "w")
    
    # Continue uploading files from where it left.
    while i < len(files):
        filepath = files[i]
        print(f"{i} -) ", end="")
        upload_file(filepath)
        save_index(i, progressfp)
        i += 1

