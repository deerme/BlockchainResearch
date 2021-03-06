from sys import stdout, path
path.append("..")

from six.moves import urllib
import json
from config.config_file import baseDir
import csv
import time
from datetime import datetime

def scrapePageOfBlocks(p, headers):
    url = f"https://api.viewblock.io/zilliqa/blocks?page={p}&network=mainnet"
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    response = json.load(response)

    blocks = response["docs"]
    return list(map(lambda b: {
        "Height": b["height"],
        "Hash": b["hash"] if "hash" in b else None,
        "Date": datetime.fromtimestamp(b["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        "Miner address": b["miner"]["address"],
        "Difficulty": float(b["difficulty"]),
        "Reward": float(b["reward"]),
        "Transactions": int(b["txCount"])
    }, blocks))

def scrapeBlocks():
    blocks = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Origin": "https://viewblock.io"
    }

    for p in range(22951, 23480):
        newBlocks = scrapePageOfBlocks(p, headers)
        blocks += newBlocks

        if p == 1:
            print(blocks[0])

        stdout.write("\r%d pages scraped" % p)
        stdout.flush()

        if p % 10 == 0:
            with open(baseDir + "/Data/OtherChains/zilliqa/historical_blocks.csv", "a") as dest:
                w = csv.DictWriter(dest, blocks[0].keys())
                if p == 10:
                    # if this is the first 20 pages, we'll need to write the headers to the csv file, then dump the data
                    w.writeheader()
                w.writerows(blocks)

            with open(baseDir + "/Logs/zilliqa/blocks.txt", "a") as logfile:
                logfile.write("%d pages scraped\n" % p)

            blocks = []
        time.sleep(0.1)
    
    with open(baseDir + "/Data/OtherChains/zilliqa/historical_blocks.csv", "a") as dest:
        w = csv.DictWriter(dest, blocks[0].keys())
        w.writerows(blocks)

    with open(baseDir + "/Logs/zilliqa/blocks.txt", "a") as logfile:
        logfile.write("%d pages of blocks scraped\n" % p)


def main():
    scrapeBlocks()

if __name__ == "__main__":
    main()