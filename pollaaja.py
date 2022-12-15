#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import argparse
import requests
import time
import smtplib
import ssl

MESSAGE = """From: pollaaja@peelo.net
To: {0}
Content-Type: text/plain; charset=utf-8
Subject: Notification!

The text "{1}" can be found from {2}.
"""

class Pollaaja():
    def __init__(self, url, text, host, port, username, password, recipient):
        self.url = url
        self.text = text
        self.recipient = recipient
        self.message = MESSAGE.format(recipient, text, url).encode("utf-8")

        self.ctx = ssl.create_default_context()
        self.server = smtplib.SMTP_SSL(host, port, self.ctx)
        self.server.login(username, password)

    def __del__(self):
        self.server.quit()

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
                self.server.sendmail(
                    "pollaaja@peelo.net",
                    [self.recipient],
                    self.message)
                break
            else:
                print("The text is not found yet!")

            time.sleep(300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Poll a website for certain text")
    parser.add_argument("-w", "--website", type=str, required=True, help="website to poll")
    parser.add_argument("-t", "--text", type=str, required=True, help="text to poll")

    parser.add_argument("-s", "--server", type=str, required=True, help="SMTP host/IP to connect")
    parser.add_argument("-p", "--port", type=str, required=False, help="SMTP port to connect", default=587)

    parser.add_argument("-u", "--username", type=str, required=True, help="SMTP user")

    parser.add_argument("-r", "--recipient", type=str, required=True, help="notification email recipient")

    args = parser.parse_args()

    pollaaja = Pollaaja(
        args.website,
        args.text,
        args.host,
        args.port,
        args.username,
        input("Type your password and press enter: "),
        args.recipient)
    pollaaja.run()
