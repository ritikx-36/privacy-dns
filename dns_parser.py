data = b'\x06google\x03com\x00'

i = 0
domain = ""

while data[i] != 0:
    length = data[i]

    i += 1

    domain += data[i:i + length].decode()

    i += length

    domain += "."

print(domain)
