from sys import stdout, path
import requests
path.append("..")

from explorers.etherscan_utils import getHtml
from datetime import datetime
import time
import os
import csv
from config.config_file import baseDir

def scrapePageOfBlocks(hi):
    blocks = []
    url = f"https://minergate.com/blockchain/bcn/blocks/{hi}"
    soup = getHtml(url)
   
    # find all the <tr/> html elements - these are table rows
    # (the first one just contains column headers so we discard it)
    rows = soup.findAll("tr")[1:]

    # extract the data from each row of the table
    for row in rows:
        tds = row.findAll("td")
        blocks.append({
            "Height": int(tds[0].a.string),
            "Date": tds[1].span.text[:19], 
            "Size": int(tds[2].string.replace(",", "")),
            "Transactions": int(tds[3].string),
            "Hash": tds[4].a.string
        })

    if hi == 2045320:
        print("\n", blocks[0])

    return blocks

def scrapeAllBlocks():
    blocks = []
    p = 11301
    hi = 2045320 - (30 * (p-1))
    while hi > 0:
        blocks += scrapePageOfBlocks(hi)

        stdout.write(f"\r{p} pages of blocks scraped ({int(100*(p/68177))}% done)")
        stdout.flush()

        if p % 100 == 0:
            # we want to save the last 5 pages to disk and then clear the working list to free up RAM
            with open(baseDir + "/Data/OtherChains/bytecoin/historical_blocks.csv", "a") as dest:
                w = csv.DictWriter(dest, blocks[0].keys())
                if p == 100:
                    # if this is the first 100 pages, we'll need to write the headers to the csv file, then dump the data
                    w.writeheader()
                w.writerows(blocks)

            with open(baseDir + "/Logs/bytecoin/blocks.txt", "a") as logfile:
                logfile.write(f"{p} pages of blocks scraped\n")

            blocks = []
        
        time.sleep(0.05)
        hi -= 30
        p += 1

def main():
    scrapeAllBlocks()

if __name__ == "__main__":
    main()