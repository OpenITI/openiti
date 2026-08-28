"""Functions to download OpenITI from GitHub or Zenodo"""

import requests
import os
import subprocess
import time
import sys


ALL_LANGUAGES = ["ARA", "PER", "URD"]

def download_file(url, dest_path, chunk_size=1024 * 1024, 
                  expected_size=None, max_retries=5, timeout=30):
    """Download a file from a URL to a destination path in chunks
    (better for large files).

    Resumes from where a previous attempt left off (via HTTP Range requests)
    and retries with exponential backoff on connection errors, so a dropped
    connection partway through a large download doesn't force a full restart.
    """
    for attempt in range(1, max_retries + 1):
        resume_from = 0
        headers = {}
        mode = "wb"

        # if the file was already partly downloaded, resume download
        # from where it left off:
        if os.path.exists(dest_path):
            resume_from = os.path.getsize(dest_path)
            headers = {"Range": f"bytes={resume_from}-"}
            mode = "ab"
        
            if expected_size and resume_from == expected_size:
                print("Already downloaded completely.")
                return
            else:
                print(resume_from, "bytes already downloaded. Resuming from there.")

        try:
            with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
                if resume_from and r.status_code != 206:
                    print("server ignored the Range request; restart from scratch")
                    resume_from = 0
                    mode = "wb"
                r.raise_for_status()
                with open(dest_path, mode) as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)

            if expected_size and os.path.getsize(dest_path) != expected_size:
                raise requests.exceptions.RequestException(
                    f"Downloaded size ({os.path.getsize(dest_path)}) does not "
                    f"match expected size ({expected_size})."
                )
            return
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise
            wait = 2 ** attempt
            print(f"Download error ({e}). Retrying in {wait}s ({attempt}/{max_retries})...")
            time.sleep(wait)

def AH_folders(dest_folder, languages="all", start_year=0, end_year=1500, overwrite=False):
    """Download xxxxAH OpenITI folders from GitHub
    and save them to a destination folder.
    
    Args:
        dest_folder (str): The folder where the downloaded files will be saved.
        languages (str or list): Languages to download. Can be "all", 
            a single language code (e.g., "PER"), 
            or a list of language codes (["ARA", "PER"]).
        start_year (int): The starting year (inclusive) for filtering folders.
        end_year (int): The ending year (inclusive) for filtering folders.
        overwrite (bool): Whether to overwrite existing folders. Defaults to False.
    """
    
    # Prepare the destination folder
    os.makedirs(dest_folder, exist_ok=True)

    # Determine the start and end folders based on the provided years
    start_idx = 1
    if start_year > 0:
        start_idx += (int(start_year)-1)//25

    end_idx = 1
    if end_year > 0:
        end_idx += (int(end_year)-1)//25

    lang_list = []
    if languages=="all":
        lang_list = ALL_LANGUAGES
    elif isinstance(languages, str):
        lang_list = languages.upper().split(",")
    elif isinstance(languages, list) or isinstance(languages, tuple) or isinstance(languages, set): 
        lang_list = languages
    elif languages==None:
        lang_list = ALL_LANGUAGES
    else:
        raise ValueError("Invalid value for 'languages'. Must be 'all', a string, or a list of three-letter language codes.")

    for lang in lang_list:
        if lang not in ALL_LANGUAGES:
            print(lang, "is not a valid three-letter language code. Skipping.")
            print(f"Valid codes are: {ALL_LANGUAGES}")
            continue

        if lang == "ARA":
            lang = ""
        for idx in range(start_idx, end_idx + 1):
            folder_name = f"{lang}{25*idx:04d}AH"
            url = f"https://github.com/OpenITI/{folder_name}.git"
            repo_path = os.path.join(dest_folder, folder_name)

            if os.path.isdir(repo_path) and not overwrite:
                print(f"{repo_path} already exists. Skipping.")
                continue

            kwargs = {"capture_output": True, "text":True}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            print(f"Cloning {url} into {repo_path}...")
            result = subprocess.run(["git", "clone", url, repo_path], **kwargs)
            if result.returncode != 0:
                print(f"Failed to clone {url}: {result.stderr.strip()}")
            else:
                print("done:", repo_path)


def from_zenodo(release_no, dest_folder, unzip=True, remove_zip=True):
    """Download a specific release of OpenITI from Zenodo and save it to the destination folder.
    Args:
        release_no (str or int): The release number to download (e.g., "2025.1.9" or 9).
        dest_folder (str): The folder where the downloaded files will be saved.
        unzip (bool): Whether to unzip the downloaded files. Defaults to True.
        remove_zip (bool): Whether to remove the zip files after unzipping.
            Defaults to True.

    Returns:
        str: The full release number (YYYY.n.n) of the downloaded version.
    """
    API_BASE = "https://zenodo.org/api/records"
    V2019_ID = "3082464"

    def get_all_versions_meta():
        """Return metadata for every published version of a record series."""
        resp = requests.get(f"{API_BASE}/{V2019_ID}/versions")
        resp.raise_for_status()
        return resp.json()["hits"]["hits"]

    def find_version(versions, release_number):
        if len(str(release_number)) > 3:
            for record in versions:
                if record.get("metadata", {}).get("version") == release_number:
                    return record
        else:
            for record in versions:
                if record.get("metadata", {}).get("version", "").split(".")[-1] == str(release_number):
                    return record
        available = [r.get("metadata", {}).get("version") for r in versions]
        raise ValueError(
            f"Release '{release_number}' not found. Available versions: {available}"
        )

    # get metadata of all versions currently in zenodo:
    versions = get_all_versions_meta()

    # find the requested release:
    record = find_version(versions, release_no)
    release_number = record.get("metadata", {}).get("version")
    print(f"Found release {release_number} -> record id {record['id']}")

    # prepare outfolder:
    os.makedirs(dest_folder, exist_ok=True)

    # download all files in the release:
    for file_entry in record["files"]:
        filename = file_entry["key"]
        download_url = file_entry["links"]["self"]
        dest_path = os.path.join(dest_folder, filename)

        if os.path.exists(dest_path) and os.path.getsize(dest_path) == file_entry["size"]:
            continue

        print(f"Downloading {filename} ({file_entry['size'] / 1e6:.1f} MB)...")
        download_file(download_url, dest_path, expected_size=file_entry["size"])
        print("Download finished.")
        if dest_path.endswith(".zip") and unzip:
            print(f"Unzipping {filename}...")
            import zipfile

            with zipfile.ZipFile(dest_path, "r") as zip_ref:
                zip_ref.extractall(dest_folder)
            print("Unzipping finished.")
            if remove_zip:
                os.remove(dest_path)
                print(f"Removed {filename}.")

    return release_number
    
if __name__ == "__main__":
    from_zenodo(9, r"C:\Users\Peter.Verkinderen\gh\OpenITI\zenodo\2025.1.9")
    #AH_folders(r"C:\Users\Peter.Verkinderen\gh\OpenITI\zenodo\2025.1.9")
