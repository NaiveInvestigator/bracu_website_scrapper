def decodeEmail(e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
        de += chr(int(e[i:i+2], 16)^k)

    return de

print(decodeEmail("bad3d4dcd5fad8c8dbd9cf94dbd994d8de"))
