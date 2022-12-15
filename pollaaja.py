#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import configparser
import requests
import time
import smtplib
import ssl


class Emailer():
    def __init__(self, host, port, username, password):
        self.username = username
        self.ctx = ssl.create_default_context()
        self.server = smtplib.SMTP(host, port)
        self.server.starttls(context=self.ctx)
        self.server.login(username, password)

    def __del__(self):
        self.server.quit()

    def send_mail(self, recipient, message):
        self.server.sendmail(self.username, [recipient], message)


class Pollaaja():
    def __init__(self, url, text, emailer, sender, recipient):
        self.url = url
        self.text = text
        self.emailer = emailer
        self.recipient = recipient
        self.message = """From: {0}
To: {1}
Content-Type: text/plain; charset=utf-8
Subject: Notification!

The text "{2}" cannot be found from {3}.
""".format(sender, recipient, text, url).encode("utf-8")

    def run(self):
        found = True

        while found:
            response = requests.get(self.url)

            print(datetime.now(), end=". HTTP status code = ")
            print(response.status_code, end=". ")

            if response.status_code != 200:
                print("Will retry in a minute")
                time.sleep(60)
                continue

            found = response.text.find(self.text) >= 0

            if not found:
                self.emailer.send(self.recipient, self.message)
                return

            print("The text is still present. No change!")
            time.sleep(300)


if __name__ == "__main__":

    config = configparser.ConfigParser(strict=False)

    try:
        config.read("pollaaja.ini")

        url = config.get("site", "url")
        text = config.get("site", "text")

        host = config.get("smtp", "host")
        port = config.getint("smtp", "port")
        user = config.get("smtp", "user")
        pwd = config.get("smtp", "pass")
        recipient = config.get("smtp", "recipient")
    except Exception as e:
        config.add_section("site")
        config["site"]["url"] = "https://google.com"
        config["site"]["text"] = "google"

        config.add_section("smtp")
        config["smtp"]["host"] = "smtp.gmail.com"
        config["smtp"]["port"] = "587"
        config["smtp"]["user"] = "from@gmail.com"
        config["smtp"]["pass"] = "password"
        config["smtp"]["recipient"] = "to@gmail.com"

        with open("pollaaja.ini", "w+") as config_file:
            config.write(config_file)

        print("Created pollaaja.ini. Please fill it out and run again.")
        print(f"Exception details: {e}")

        exit(2)

    emailer = Emailer(host, port, user, pwd)

    poller = Pollaaja(url, text, emailer, user, recipient)

    poller.run()
