# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Tim Cocks for CircuitPython Organization
#
# SPDX-License-Identifier: MIT
"""
`size_tools`
================================================================================

Tools for measuring library size and memory usage.


* Author(s): Tim Cocks

Implementation Notes
--------------------

"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/circuitpython/CircuitPython_Org_size_tools.git"

import os
import zipfile
import requests
import toml


def download_latest_bundle():
    """
    download teh latest bundle zip and extract it.

    :return: string download_filename: the name of downloaded bundle zip file.
    """
    json_resp = requests.get(
        "https://api.github.com/repos/adafruit/Adafruit_CircuitPython_Bundle/releases/latest"
    ).json()

    for asset in json_resp["assets"]:
        if "adafruit-circuitpython-bundle-8" in asset["name"]:
            # print(asset["browser_download_url"])
            bundle_zip = requests.get(
                asset["browser_download_url"], allow_redirects=True
            )
            download_filename = asset["browser_download_url"].split("/")[-1]

            with open(download_filename, "wb") as bundle_out:
                bundle_out.write(bundle_zip.content)
                bundle_out.close()
            with zipfile.ZipFile(download_filename, "r") as zip_ref:
                zip_ref.extractall(".")
            # shutil.move(f'{download_filename.replace(".zip", "")}/lib/', ".")
            # shutil.move(f'{download_filename.replace(".zip", "")}/examples/', ".")
    return download_filename


def find_v8_mpy_zip():
    """
    find the version 8 mpy bundle in the current directory.
    :return:
    """
    for file in os.listdir("./"):
        if "8.x-mpy" in file:
            # print("Found 8.x mpy zip:")
            # print(file)
            return file

    return None


def get_sizes_from_dir(dir_path, verbose=False):
    """
    Total up the sizes and string sizes of all files inside of a directory.

    :param dir_path: directory to check sizes in.
    :param verbose: pass True to print additional information.
    :return: tuple(int, int): the total sum of file sizes and the
    total sum of strings within those files.
    """
    total_size = 0
    total_strings_size = 0

    for subdir_tuple in os.walk(dir_path):
        for mpy_file in subdir_tuple[2]:
            cur_file_path = f"{subdir_tuple[0]}{'/' if subdir_tuple[0][-1] != '/' else ''}{mpy_file}"
            if verbose:
                print(f"cur file: {cur_file_path}")

            file_stats = os.stat(cur_file_path)
            total_size += file_stats.st_size
            if verbose:
                print(f"size: {file_stats.st_size}")
            os.system(f"strings {cur_file_path} > strings_output.txt")
            os.system(f"strings {cur_file_path} >> totaled_strings_output.txt")
            string_file_stats = os.stat("strings_output.txt")
            total_strings_size += string_file_stats.st_size
            if verbose:
                print(f"strings size: {string_file_stats.st_size}")
                if string_file_stats.st_size != 0:
                    print(
                        f"percent: {string_file_stats.st_size / file_stats.st_size * 100.0:.2f}%"
                    )

    return total_size, total_strings_size


def measure_sizes():
    """
    Run from CLI in a modified circuitpython library repo that has mpy files built already.
    Prints a report showing the size of the mpy file(s) and the size of the
    strings within. Also calculates and prints the sizes for the current version
    of the library.

    :return: None
    """
    # read module name from pyproject.toml
    pyproject_data = toml.load("pyproject.toml")
    if "packages" in pyproject_data["tool"]["setuptools"]:

        module_name = pyproject_data["tool"]["setuptools"]["packages"][0]
    elif "py-modules" in pyproject_data["tool"]["setuptools"]:
        module_name = pyproject_data["tool"]["setuptools"]["py-modules"][0]

    # New Version:
    found_v8_mpy_zip = find_v8_mpy_zip()
    os.chdir(found_v8_mpy_zip)
    os.chdir(os.listdir("./")[0])
    os.chdir("lib")

    if os.path.isfile(os.listdir("./")[0]):
        mpy_file = os.listdir("./")[0]
        file_stats = os.stat(mpy_file)
        print("This Branch Version:")
        print(f"mpy file size: {file_stats.st_size} bytes")

        # command = ['strings', mpy_file]
        # p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.)
        # strings_command_output = p.stdout.read()
        # retcode = p.wait()

        os.system(f"strings {mpy_file} > strings_output.txt")
        string_file_stats = os.stat("strings_output.txt")
        print(f"strings output size: {string_file_stats.st_size} bytes")
        print(
            f"strings percentage of mpy: "
            f"{(string_file_stats.st_size / file_stats.st_size) * 100.0:.2f}%"
        )
    else:
        os.chdir(os.listdir("./")[0])
        file_size, strings_size = get_sizes_from_dir("./", verbose=False)
        print("This Branch Version:")
        print(f"total mpy files size: {file_size} bytes")
        print(f"strings output size: {strings_size} bytes")
        if file_size != 0:
            print(
                f"strings percentage of mpy: {(strings_size / file_size) * 100.0:.2f}%"
            )

    # Published Version:
    print()
    print("---")
    print()
    print("Published Version:")
    downloaded_filename = download_latest_bundle()
    os.chdir(downloaded_filename.replace(".zip", ""))
    os.chdir("lib")
    single_mpy_file = f"./{module_name}.mpy"
    if os.path.exists(single_mpy_file):
        # if it's a single mpy file

        file_stats = os.stat(single_mpy_file)
        print(f"mpy file size: {file_stats.st_size} bytes")
        os.system(f"strings {single_mpy_file} > published_strings_output.txt")
        string_file_stats = os.stat("published_strings_output.txt")
        print(f"strings output size: {string_file_stats.st_size} bytes")
        print(
            f"strings percentage of mpy: {(string_file_stats.st_size / file_stats.st_size) * 100.0:.2f}%"
        )

    else:  # single mpy file not found
        package_name = single_mpy_file.replace(".mpy", "")
        os.chdir(package_name)
        file_size, strings_size = get_sizes_from_dir("./", verbose=False)

        print(f"total mpy files size: {file_size} bytes")
        print(f"strings output size: {strings_size} bytes")
        if file_size != 0:
            print(
                f"strings percentage of mpy: {(strings_size / file_size) * 100.0:.2f}%"
            )


if __name__ == "__main__":
    measure_sizes()
