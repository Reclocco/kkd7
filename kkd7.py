import math
import os
import random
import sys

errors = 0
codes = ["00000000", "00011110", "00100111", "00111001", "01001011", "01010101", "01101100", "01110010", "10001101",
         "10010011", "10101010", "10110100", "11000110", "11011000", "11100001", "11111111"]


def bit_change(byte):
    chain = format(int.from_bytes(byte, byteorder='little'), 'b').zfill(8)
    number = 0

    for i in range(len(chain)):
        bit = chain[i]
        if random.random() < float(sys.argv[2]):
            if chain[i] == "0":
                bit = "1"
            else:
                bit = "0"
        if bit == "1":
            number += 2 ** (7 - i)

    return number.to_bytes(1, 'little')


def encode(byte):
    num1 = []
    num2 = []

    out1 = 0
    out2 = 0

    chain = format(int.from_bytes(byte, byteorder='little'), 'b').zfill(8)

    for i in range(4):
        num1.append(int(chain[i]))
        num2.append(int(chain[i + 4]))

    num1.append((num1[0] + num1[1] + num1[3]) % 2)
    num2.append((num2[0] + num2[1] + num2[3]) % 2)

    num1.append((num1[0] + num1[2] + num1[3]) % 2)
    num2.append((num2[0] + num2[2] + num2[3]) % 2)

    num1.append((num1[1] + num1[2] + num1[3]) % 2)
    num2.append((num2[1] + num2[2] + num2[3]) % 2)

    num1.append(sum(num1) % 2)
    num2.append(sum(num2) % 2)

    for i in range(8):
        out1 += (2 ** (7 - i)) * num1[i]
        out2 += (2 ** (7 - i)) * num2[i]

    return out1.to_bytes(1, 'little'), out2.to_bytes(1, 'little')


def decode(byte1, byte2):
    global codes
    global errors

    chain1 = format(int.from_bytes(byte1, byteorder='little'), 'b').zfill(8)
    chain2 = format(int.from_bytes(byte2, byteorder='little'), 'b').zfill(8)

    chain_dif1 = []
    chain_dif2 = []

    for i in range(16):
        counter1 = 0
        counter2 = 0
        for j in range(8):
            if codes[i][j] != chain1[j]:
                counter1 += 1
            if codes[i][j] != chain2[j]:
                counter2 += 1
        chain_dif1.append(counter1)
        chain_dif2.append(counter2)

    if min(chain_dif1) == 2:
        errors += 1
    if min(chain_dif2) == 2:
        errors += 1

    chain1 = codes[chain_dif1.index(min(chain_dif1))]
    chain2 = codes[chain_dif2.index(min(chain_dif2))]

    outcome = 0

    for i in range(4):
        if chain1[i] == "1":
            outcome += 2 ** (7 - i)
        if chain2[i] == "1":
            outcome += 2 ** (3 - i)

    return outcome.to_bytes(1, 'little')


def bit_chunk_checker(byte1, byte2):
    chain1 = format(int.from_bytes(byte1, byteorder='little'), 'b').zfill(8)
    chain2 = format(int.from_bytes(byte2, byteorder='little'), 'b').zfill(8)
    outcome = 0

    if chain1[0] != chain2[0] or chain1[1] != chain2[1] or chain1[2] != chain2[2] or chain1[3] != chain2[3]:
        outcome += 1
    if chain1[4] != chain2[4] or chain1[5] != chain2[5] or chain1[6] != chain2[6] or chain1[7] != chain2[7]:
        outcome += 1
    return outcome


def noise():
    encoded = open(sys.argv[3], "rb")
    decoded = open(sys.argv[4], "rb")

    byte = encoded.read(1)
    while byte:
        decoded.write(bit_change(byte))
        byte = encoded.read(1)


def check():
    encoded = open(sys.argv[2], "rb")
    decoded = open(sys.argv[3], "rb")

    different_bytes = math.fabs(os.path.getsize(sys.argv[2]) - os.path.getsize(sys.argv[3])) * 2
    if os.path.getsize(sys.argv[2]) < os.path.getsize(sys.argv[3]):
        length = os.path.getsize(sys.argv[2])
    else:
        length = os.path.getsize(sys.argv[3])

    for _ in range(length):
        byte_2 = decoded.read(1)
        byte_1 = encoded.read(1)
        different_bytes += bit_chunk_checker(byte_1, byte_2)

    print("Number of different 4 bit packs: ", int(different_bytes))


def encoder():
    raw = open(sys.argv[2], "rb")
    encoded = open(sys.argv[3], "wb")

    byte = raw.read(1)
    while byte:
        b1, b2 = encode(byte)
        encoded.write(b1)
        encoded.write(b2)
        byte = raw.read(1)


def decoder():
    global errors

    encoded = open(sys.argv[2], "rb")
    decoded = open(sys.argv[3], "wb")

    byte1 = encoded.read(1)
    byte2 = encoded.read(1)
    while byte1:
        decoded.write(decode(byte1, byte2))
        byte1 = encoded.read(1)
        byte2 = encoded.read(1)
    print("Double errors: ", errors)


def main():
    if sys.argv[1] == 'noise':
        noise()
    elif sys.argv[1] == 'check':
        check()
    elif sys.argv[1] == 'encoder':
        encoder()
    elif sys.argv[1] == 'decoder':
        decoder()


main()
