#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import argparse
import requests
import time

class Pollaaja():
    def __init__(self, url, text):
        self.url = url
        self.text = text

    def run(self):

        found = False

        while not found:
            response = requests.get(self.url)

            print(datetime.now(), end=". HTTP status code = ")
            print(response.status_code, end=". ")

            if response.status_code != 200:
                print("Will retry in a minute")
                time.sleep(60)
                continue

            found = response.text.find(self.text) >= 0

            if found:
                print("Huzzah!")
                break
            else:
                print("The text is not found yet!")

            time.sleep(300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poll a website for certain text")
    parser.add_argument("-w", "--website", type=str, required=True, help="website to poll")
    parser.add_argument("-t", "--text", type=str, required=True, help="text to poll")

    args = parser.parse_args()

    pollaaja = Pollaaja(args.website, args.text)
    pollaaja.run()
