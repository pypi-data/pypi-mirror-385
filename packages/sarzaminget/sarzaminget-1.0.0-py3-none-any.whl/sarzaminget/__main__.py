#!/usr/bin/env python3
"""IR downloader"""

# SPDX-License-Identifier: 0BSD
# SPDX-FileCopyrightText: 2025 NexusSfan <nexussfan@duck.com>

import argparse
import re
import sys
import requests
from yt_dlp import YoutubeDL
from bs4 import BeautifulSoup
from tqdm import tqdm

__import__("lxml")  # check for lxml

__version__ = "1.0.0"
FULL_TITLE = f"sarzaminget {__version__}"
headers = {"User-Agent": FULL_TITLE}


def arguments():
    parser = argparse.ArgumentParser(prog="sarzaminget", description="IR Downloader")
    parser.add_argument("link", help="SarzaminDownload link")
    parser.add_argument("-V", "--verbose", help="Verbose mode", action="store_true")
    parser.add_argument(
        "-v", "--version", help="version", action="version", version=FULL_TITLE
    )
    return parser.parse_args()

args = arguments()
verbose = args.verbose

def log(printed):
    if verbose:
        print(printed)

def get_links_sarzamindownload(url):
    log(f"Loading {url}")
    site = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(site.text, features="lxml")
    log("Checking for links")
    all_links = soup.find_all("a")
    sarzamin_links = []
    title_for_links = []
    for some_links in all_links:
        if some_links.attrs.get("href"):
            if "wikishare.ir" in some_links.attrs["href"]:
                log(f"Found link {some_links.attrs["href"]} with title {some_links.string}")
                sarzamin_links.append(some_links.attrs["href"])
                title_for_links.append(some_links.string)
    return sarzamin_links, title_for_links

def download_todl(links_to_dl, titles_to_dl):
    for linkno, link in enumerate(links_to_dl):
        print(f"Downloading {titles_to_dl[linkno]}...")
        r = requests.get(link, stream=True, allow_redirects=True, headers=headers)
        total_size = int(r.headers.get("Content-Length", 0))
        block_size = 1024
        raw_url = link.split("?")[0]
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(raw_url.split("/")[-1], "wb") as file:
                for data in r.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)


def sarzamindownload_dl(url):
    links, titles = get_links_sarzamindownload(url)
    if len(links) > 1:
        print("There are multiple links")
        for linknumber, link in enumerate(links):
            print(f"#{linknumber} - {titles[linknumber]} - {link}")
        print("Please select which one you want to download")
        print("(seperated by commas, no spaces please)")
        to_dl = [int(i) for i in input().split(",")]
    elif len(links) == 0:
        print("No links found!")
        sys.exit(1)
    else:
        to_dl = [0]
    links_to_dl = [links[l] for l in to_dl]
    titles_to_dl = [titles[l] for l in to_dl]
    download_todl(links_to_dl, titles_to_dl)

if __name__ == "__main__":
    if re.match(r"^https?:\/\/(?:www\.)?sarzamindownload\.com\/.*", args.link):
        sarzamindownload_dl(args.link)
    if re.match(r"^https?:\/\/(?:www\.)?aparat\.com\/.*", args.link):
        with YoutubeDL() as ydl:
            ydl.download(args.link)