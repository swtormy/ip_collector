from seleniumwire import webdriver
import threading
import time
import urllib.parse
import socket
import dns.resolver
import requests
from selenium.webdriver.chrome.options import Options


# Function to get the IP address of a given URL
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


# Function to continuously collect IPs until a stop event is signaled
def collect_ips(browser_driver, collected_ips, stop_signal):
    while not stop_signal.is_set():
        for request in browser_driver.requests:
            if request.response:
                ip = get_ip(request.url)
                if ip not in collected_ips:
                    collected_ips.append(ip)
        time.sleep(1)


# Function to save the collected IPs to a file
def save_ips_to_file(collected_ips, filename):
    with open(filename, 'w') as file:
        for ip in collected_ips:
            file.write(f"{ip}\n")


# Chrome options to suppress logging
chrome_options = Options()
chrome_options.add_argument("--log-level=3")

# Create a new Selenium Chrome webdriver instance
browser_driver = webdriver.Chrome(options=chrome_options)

# Navigate to the target webpage
browser_driver.get('https://www.github.com')

# Create an empty list to store the collected IPs
collected_ips = []


# Create a stop event for the IP collection thread
stop_signal = threading.Event()

# Create and start the IP collection thread
ip_collection_thread = threading.Thread(target=collect_ips, args=(browser_driver, collected_ips, stop_signal))
ip_collection_thread.start()

# Wait for the user to finish browsing before stopping the IP collection thread
input("Press Enter when you're done browsing to stop the script...")
stop_signal.set()
ip_collection_thread.join()

# Save the collected IPs to a file
save_ips_to_file(collected_ips, 'ips.txt')
