import hmac, base64, struct, hashlib, time


def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h


def get_totp_token(secret):
    return get_hotp_token(secret, intervals_no=int(time.time())//30)

import qrcode

st = 'otpauth://totp/{name}?secret={code}'.format(name = 'Ilnur',code = 'MZXW633PN5XW6MZV')
img = qrcode.make(st)
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")



secret = 'MZXW633PN5XW6MZV'
key = ''
while True:

    if key != get_totp_token(secret):
        print (get_totp_token(secret))
        key = get_totp_token(secret)
    time.sleep(1)