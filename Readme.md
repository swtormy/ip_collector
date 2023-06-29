# Webpage IP Collector

This Python script uses Selenium to collect IP addresses from the network traffic that occurs when browsing a webpage. This can be especially useful for understanding the services a web page relies on and can assist in debugging and cybersecurity applications.

## Overview

1. The script launches a Selenium controlled Chrome browser instance and navigates to a target website.
2. It spawns a separate thread that continuously collects IP addresses associated with requests made by the Selenium controlled browser.
3. Once you've finished browsing, the script will stop collecting IP addresses, write them to a file, and then terminate.

## Prerequisites

The script requires the following:

- Python 3.x
- Selenium
- Selenium Wire
- dns.resolver
- Requests
- Threading

## Execution

To run the script, use a Python interpreter. Once you're done browsing, press Enter in the terminal to stop the script. The collected IP addresses will be written to a file.

---

## Refactored Code

Here is the refactored code with clear variable descriptions:

```python
from seleniumwire import webdriver
import threading
import time
import urllib.parse
import socket
import dns.resolver
import requests
from selenium.webdriver.chrome.options import Options

def get_ip(target_url, postfix='/32'):
    hostname = urllib.parse.urlparse(target_url).hostname
    try:
        return socket.gethostbyname(hostname) + postfix
    except socket.gaierror:
        response = requests.head(target_url, allow_redirects=True)
        try:
            return response.headers['Host'] + postfix
        except KeyError:
            try:
                dns_answers = dns.resolver.query(hostname, 'A')
                for rdata in dns_answers:
                    return  rdata.address + postfix
            except dns.resolver.NXDOMAIN:
                print('IP not found:', target_url)

def collect_ips(browser_driver, collected_ips, stop_signal):
    while not stop_signal.is_set():
        for request in browser_driver.requests:
            if request.response:
                ip = get_ip(request.url)
                if ip not in collected_ips:
                    collected_ips.append(ip)
        time.sleep(1)

def save_ips_to_file(collected_ips, filename):
    with open(filename, 'w') as file:
        for ip in collected_ips:
            file.write(f"{ip}\n")

chrome_options = Options()
chrome_options.add_argument("--log-level=3")

browser_driver = webdriver.Chrome(options=chrome_options)
browser_driver.get('https://www.github.com')
collected_ips = []

stop_signal = threading.Event()
ip_collection_thread = threading.Thread(target=collect_ips, args=(browser_driver, collected_ips, stop_signal))
ip_collection_thread.start()

input("Press Enter when you're done browsing to stop the script...")
stop_signal.set()
ip_collection_thread.join()
save_ips_to_file(collected_ips, 'ips.txt')
```