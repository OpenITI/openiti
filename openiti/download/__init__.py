"""Functions to download (parts of) the OpenITI corpus from GitHub or Zenodo.

Usage:
    >>> from openiti import download
    >>> folder = "C:/Downloads/OpenITI/release")
    >>> download.from_zenodo("2025.1.9", folder, unzip=True)
    >>> folder = "C:/Downloads/OpenITI/current/ARA")
    >>> download.clone_AH_repos(folder, languages="ARA", start_year=300, end_year=400
    >>> folder = "C:/Downloads/OpenITI/current/MSS")
    >>> download.clone_MSS_repo(folder)
    >>> folder = "C:/Downloads/OpenITI/metadata"
    >>> download.metadata("2025.1.9", folder)
    >>> folder = "C:/Downloads/OpenITI/metadata"
    >>> download.metadata("current", folder)
"""

import os
import re
import requests
import shutil
import subprocess
import sys
import time

ALL_LANGUAGES = ["ARA", "PER", "URD"]

def download_file(url, dest_path, chunk_size=1024 * 1024, 
                  expected_size=None, max_retries=10, timeout=60):
    """Download a file from a URL to a destination path in chunks
    (better for large files).

    Resumes from where a previous attempt left off (via HTTP Range requests)
    and retries with exponential backoff on connection errors, so a dropped
    connection partway through a large download doesn't force a full restart.
    """
    # determine the style of progress printing:
    # (in IDLE, \r does not overwrite the previous line)
    if "idlelib" in sys.modules:
        line_end = "\n"
    else:
        line_end = "\r"

    for attempt in range(0, max_retries + 1):
        headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/124.0.0.0 Safari/537.36"
        }
        # if the file was already partly downloaded, resume download
        # from where it left off:
        if os.path.exists(dest_path):
            mode = "ab"
            resume_from = os.path.getsize(dest_path)        
            if expected_size and resume_from == expected_size:
                print("Already downloaded completely.")
                return
            else:
                print(resume_from, "bytes already downloaded. Resuming from there.")
                headers["Range"] = f"bytes={resume_from}-"
        else:
            mode = "wb"
            resume_from = 0

        try:
            with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
                if resume_from and r.status_code != 206:
                    print("server ignored the Range request; restart from scratch")
                    resume_from = 0
                    mode = "wb"
                    del headers["Range"]
                r.raise_for_status()
                with open(dest_path, mode) as f:
                    downloaded = resume_from
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded += chunk_size
                        if expected_size:
                            pct = int(100*downloaded/expected_size)
                            msg = f"Downloaded: {downloaded}/{expected_size} bytes ({pct}%)"
                        else:
                            msg = f"Downloaded: {downloaded} bytes"
                        print(msg, end=line_end)
                    print()
                    print("Done:", dest_path)

            if expected_size and os.path.getsize(dest_path) != expected_size:
                raise requests.exceptions.RequestException(
                    f"Downloaded size ({os.path.getsize(dest_path)}) does not "
                    f"match expected size ({expected_size})."
                )
            return
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise
            wait = 2 ** (attempt + 1)
            print(f"Download error ({e}). Retrying in {wait}s ({attempt+1}/{max_retries})...")
            time.sleep(wait)

def clone(url, dest_folder, repo_folder_name=None, overwrite=False):
    """Clone a GitHub/GitLab repo and save it to dest_folder.

    Args:
        url (str): url of the repo on GitHub/GitLab
        dest_folder (str): path of the folder in which the repo
            must be saved
        repo_folder_name (str): by default (repo_folder_name=None),
            the repo will be saved inside dest_folder
            in a subfolder with the same name as the GitHub/GitLab repo.
            If you want the subfolder to have a different name,
            set repo_folder_name.
        overwrite(bool): Whether to overwrite existing folders.
            Defaults to False.
    """
    # create the destination folder if it does not yet exist:
    os.makedirs(dest_folder, exist_ok=True)

    # create the path to the final destination folder:
    if not repo_folder_name:
        repo_folder_name = url.split("/")[-1].split(".git")[0]
    out_folder = os.path.join(dest_folder, repo_folder_name)

    # skip download if the out_folder already exists and was fully downloaded:
    if os.path.exists(os.path.join(out_folder, ".git")) and not overwrite:
        print(f"{out_folder} already exists. Skipping.")
        return

    # clone into a temp folder, so a failed/interrupted clone
    # never leaves a half-downloaded out_folder behind
    tmp_folder = out_folder + ".tmp"
    # clear any leftover temp dir from a crashed previous attempt before starting
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder, ignore_errors=True)

    # avoid opening a cmd window on Windows:
    kwargs = {"capture_output" : True, "text" : True}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    # clone into the temp folder:
    try:
        print(f"Cloning {url} into a temp folder {tmp_folder}...", )
        result = subprocess.run(["git", "clone", url, tmp_folder], **kwargs)
        if result.returncode != 0:
            print(f"\n-> Failed to clone {url}: {result.stderr.strip()}")
            return

        if os.path.exists(out_folder):
            shutil.rmtree(out_folder)
        os.rename(tmp_folder, out_folder)
        print("...renamed temp folder to", out_folder)
    finally:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder, ignore_errors=True)
    

def clone_MSS_repo(dest_folder, overwrite=False):
    """Download the manuscripts repo MSS from GitHub
    and save it to a destination folder.
    
    Args:
        dest_folder (str): The folder where the MSS repo will be saved.
        overwrite (bool): Whether to overwrite existing folders.
            Defaults to False.
    """
    url = url = f"https://github.com/OpenITI/MSS.git"
    clone(url, dest_folder, overwrite=overwrite)

def clone_AH_repos(dest_folder, languages="all", start_year=0, end_year=1500, overwrite=False):
    """Download xxxxAH OpenITI folders from GitHub
    and save them to a destination folder.
    
    Args:
        dest_folder (str): The folder where the downloaded files will be saved.
        languages (str or list): Languages to download. Can be "all", 
            a single language code (e.g., "PER"), 
            or a list of language codes (["ARA", "PER"]).
        start_year (int): The starting year (inclusive) for filtering folders.
        end_year (int): The ending year (inclusive) for filtering folders.
        overwrite (bool): Whether to overwrite existing folders.
            Defaults to False.
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
    if languages=="all" or languages is None:
        lang_list = ALL_LANGUAGES
    elif isinstance(languages, str):
        lang_list = languages.upper().split(",")
    elif isinstance(languages, list) or isinstance(languages, tuple) or isinstance(languages, set): 
        lang_list = languages
    else:
        msg = "Invalid value for 'languages'."
        msg+= "Must be 'all', a string, or a list of three-letter language codes."
        raise ValueError(msg)

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
            clone(url, dest_folder, overwrite=False)

def unzip_via_temp(zip_fp, dest_folder, remove_zip=True):
    """Unzip a zip file via a temp folder - to avoid partial unzips.

    Args:
        zip_fp (str): path to the zip file
        dest_folder (str): path to the folder where it should be unzipped
        remove_zip (bool): remove the zip file after successful unzipping

    Returns:
        None
    """
    if os.path.exists(zip_fp[:-4]):
        print("Folder already exists. Aborting unzip.")
        return
        
    tmp_folder = zip_fp + ".tmp"
    # Remove the temp folder if it already exists (partially unzipped?):
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)

    zip_fn = os.path.basename(zip_fp)        
    print(f"Unzipping {zip_fn} to a temp folder: {tmp_folder}...")
    import zipfile
    with zipfile.ZipFile(zip_fp, "r") as zip_ref:
        zip_ref.extractall(tmp_folder)

    print(f"Renaming the temp folder...")

    # remove unnecessary duplicate layers in folder hierarchy (e.g., data/data)
    folder_name = zip_fn[:-4]
    rename_path = tmp_folder
    zip_level_1 = os.listdir(tmp_folder)
    if len(zip_level_1) == 1:
        zip_level_1_pth = os.path.join(tmp_folder, zip_level_1[0])
        if os.path.isdir(zip_level_1_pth):
            zip_level_2 = os.listdir(zip_level_1_pth)
            if len(zip_level_2) == 1:
                zip_level_2_pth = os.path.join(zip_level_1_pth, zip_level_2[0])
                if os.path.isdir(zip_level_2_pth):
                    folder_name = zip_level_2[0]
                    rename_path = zip_level_2_pth
            else:
                folder_name = zip_level_1[0]
                rename_path = zip_level_1_pth
    try:
        dest_fp = os.path.join(dest_folder, folder_name)
        os.rename(rename_path, dest_fp)
    except Exception as e:
        print("Renaming failed:", e)
        print("Please rename the temp folder manually:", tmp_folder)
        return
    print("Unzipping finished:", dest_fp)
    if not rename_path == tmp_folder:
        shutil.rmtree(tmp_folder)
    if remove_zip:
        os.remove(zip_fp)
        print(f"Removed {zip_fn}.")
    

def from_zenodo(release_no, dest_folder, unzip=True, remove_zip=True):
    """Download a specific release of OpenITI from Zenodo
    and save it to the destination folder.

    Args:
        release_no (str or int): The release number to download
            (e.g., "2025.1.9" or 9).
        dest_folder (str): The folder where the downloaded files will be saved.
            A subfolder named {release_no} will be created in this folder.
        unzip (bool): Whether to unzip the downloaded files. Defaults to True.
        remove_zip (bool): Whether to remove the zip files
            after successful unzipping. Defaults to True.

    Returns:
        str: The full release number (YYYY.n.n) of the downloaded version.
    """
    
    def get_all_versions_meta(API_BASE, one_version_id):
        """Return metadata for every published version of a record.

        Returns:
            list of version dictionaries
        """
        resp = requests.get(f"{API_BASE}/{one_version_id}/versions")
        resp.raise_for_status()
        return resp.json()["hits"]["hits"]

    def find_version(versions, release_number, retried=False):
        if len(str(release_number)) > 3:
            release_number = release_number.replace("v", "")
            for record in versions:
                if record.get("metadata", {}).get("version") == release_number:
                    return record
        else:
            for record in versions:
                if record.get("metadata", {}).get("version", "").split(".")[-1] == str(release_number):
                    return record

        # if the release number was not found, check for new releases via the Zenodo API:
        if not retried:
            API_BASE = "https://zenodo.org/api/records"
            V2019_ID = "3082464"
            all_versions_from_api = get_all_versions_meta(API_BASE, V2019_ID)
            return find_version(all_versions_from_api, release_number, retried=True)
        else:
            available = [r.get("metadata", {}).get("version") for r in versions]
            raise ValueError(
                 f"Release '{release_number}' not found. Available versions: {available}"
            )

    def normalize_filename(filename):
        # Remove any OpenITI/RELEASE prefixes:
        filename = re.sub(r"OpenITI[/\-_]|RELEASE[/\-_]", "", filename)

        # remove the release_number from the filename; it will be part of the path:
        filename = re.sub(r"[-_]?v?"+release_number, "", filename)
            
        return filename
        
    # load Zenodo release metadata:
    _HERE = os.path.dirname(os.path.abspath(__file__))
    json_fp = os.path.join(_HERE, "zenodo_releases.json")
    import json
    with open(json_fp, "r", encoding="utf-8") as file:
        versions = json.load(file)

    # find the requested release:
    print("Finding the URL for the release on Zenodo...")
    record = find_version(versions, release_no)
    release_number = record.get("metadata", {}).get("version").replace("v", "")
    print(f"Found release {release_number} -> record id {record['id']}")

    # prepare outfolder:
    if release_number not in dest_folder:
        dest_folder = os.path.join(dest_folder, release_number)
    os.makedirs(dest_folder, exist_ok=True)

    # download all files in the release:
    for file_entry in record["files"]:
        outfilename = normalize_filename(file_entry["key"])        
        dest_path = os.path.join(dest_folder, outfilename)
        
        # skip if it was already downloaded in its entirety:
        if os.path.exists(dest_path) and os.path.getsize(dest_path) == file_entry["size"]:
            continue

        print(f"Downloading {outfilename} ({file_entry['size'] / 1e6:.1f} MB)...")
        download_url = file_entry["links"]["self"]
        download_file(download_url, dest_path, expected_size=file_entry["size"])
        print("Download finished.")
        if dest_path.endswith(".zip") and unzip:
            unzip_via_temp(dest_path, dest_folder, remove_zip=remove_zip)
            
    return release_number

def metadata(release_no, dest_folder, merged=True, overwrite=False):
    """Download metadata for a specific OpenITI release
    or for the current live version of the corpus on GitHub.

    Args:
        release_no (str): OpenITI release number (e.g., 2025.1.9), or "current"
        dest_folder (str): path to the folder in which the metadata file will be saved
        merged (bool): Some OpenITI releases contain two versions of the metadata file:
            one in which metadata for very large texts (too large for GitHub,
            so they were split into multiple parts) was merged,
            and one in which each part of such a large text
            has its own row in the table. For most statistical analysis,
            the merged metadata is the best fit; but if you plan to use the paths
            to the text files, you have to use the unmerged metadata (merged=False).

    Returns:
        str: path to the downloaded csv file
    """
    def build_dest_fp(dest_folder, fn, overwrite):
        do_download = True
        dest_fp = os.path.join(dest_folder, fn)
        if os.path.exists(dest_fp):
            print("File already exists:", dest_fp)
            if overwrite:
                print("-> overwriting")
                os.remove(dest_fp)
            else:
                print("-> aborting download. Re-run with `overwrite=True`")
                do_download = False
        return dest_fp, do_download
        
    base_url = "https://github.com/OpenITI/kitab-metadata-automation/raw/refs/heads/master/"
    if release_no == "current":
        fn = "OpenITI_Github_clone_metadata_light.csv"
        url = base_url+"output/"+fn
        # add a time stamp (YYYY-MM-DD) to the output filename:
        fn = fn.replace(".csv", f'_{time.strftime("%Y-%m-%d")}.csv')
        dest_fp, do_download = build_dest_fp(dest_folder, fn, overwrite)
        if do_download:
            download_file(url, dest_fp)
    else:
        fn = f"OpenITI_metadata_{release_no.replace('.', '-')}.csv"
        download_unmerged = True
        if merged:
            try:
                merged_fn = fn.replace(".csv", "_merged.csv")
                dest_fp, do_download = build_dest_fp(dest_folder, merged_fn, overwrite)
                if do_download:
                    download_file(base_url+"releases/"+merged_fn, dest_fp)
                    download_unmerged = False
            except:
                # no merged version exists; we'll download the unmerged version
                pass
            
        if download_unmerged:
            dest_fp, do_download = build_dest_fp(dest_folder, fn, overwrite)
            if do_download:
                download_file(base_url+"releases/"+fn, dest_fp)
    return dest_fp
        
