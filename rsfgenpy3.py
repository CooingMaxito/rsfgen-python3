import struct
import binascii
import argparse

# Set up the CLI parser and generate help
parser = argparse.ArgumentParser(description='RSF file generator for 3DS exheader manipulation')
parser.add_argument('-r', '--rom', help='3DS rom file', metavar='FILE', required=True, nargs=1)
parser.add_argument('-e', '--exheader', help='decrypted exheader.bin file', metavar='FILE', required=True, nargs=1)
parser.add_argument('-o', '--rsf', help='RSF file to use as a template and to write to', metavar='FILE', required=True, nargs=1)
parser.add_argument('-f', '--regionfree', help='icon.bin file to apply region free patch', metavar='FILE', nargs=1)
parser.add_argument('-s', '--spoof', action='store_true', help='apply firmware spoofing')

args = parser.parse_args()

with open(args.rom[0], "rb") as f:
    f.seek(0x1109)  # UniqueId
    uid = f.read(4)
    uid = binascii.hexlify(uid).decode()[::-1]
    c = list(uid)
    c[::2], c[1::2] = c[1::2], c[::2]
    uid = "".join(c)

    f.seek(0x1110)  # CompanyCode
    read = f.read(2)
    ccode = "".join(x.decode() for x in struct.unpack('<cc', read))

    f.seek(0x1150)  # ProductCode
    read = f.read(10)
    pcode = "".join(x.decode() for x in struct.unpack('<' + 'c'*10, read))
    pcode = pcode.rstrip(' \0')

    with open(args.exheader[0], "rb") as f:
        f.seek(0)  # Title
        read = f.read(8)
        title = "".join(x.decode() for x in struct.unpack('<' + 'c'*8, read))
        title = title.rstrip(' \0')

        f.seek(0xE)  # Remaster version
        rver = binascii.hexlify(f.read(2)).decode()[::-1]
        c = list(rver)
        c[::2], c[1::2] = c[1::2], c[::2]
        rver = "".join(c)

        f.seek(0x1C)  # Stacksize
        stack = binascii.hexlify(f.read(4)).decode()[::-1]
        c = list(stack)
        c[::2], c[1::2] = c[1::2], c[::2]
        stack = "".join(c)

        f.seek(0x40)  # Dependencies
        dep = []
        for i in range(48):
            chunk = binascii.hexlify(f.read(8)).decode()[::-1]
            c = list(chunk)
            c[::2], c[1::2] = c[1::2], c[::2]
            dep.append("".join(c))

        f.seek(0x247)  # Uses extended save data access?
        uext = binascii.hexlify(f.read(1)).decode()

        if uext == "00":
            f.seek(0x230)  # ExtSaveDataId
            exts = binascii.hexlify(f.read(8)).decode()[::-1]
            c = list(exts)
            c[::2], c[1::2] = c[1::2], c[::2]
            exts = "".join(c)

            f.seek(0x238)
            ssid1 = binascii.hexlify(f.read(4)).decode()[::-1]
            c = list(ssid1)
            c[::2], c[1::2] = c[1::2], c[::2]
            ssid1 = "".join(c)

            f.seek(0x23C)
            ssid2 = binascii.hexlify(f.read(4)).decode()[::-1]
            c = list(ssid2)
            c[::2], c[1::2] = c[1::2], c[::2]
            ssid2 = "".join(c)

            f.seek(0x240)
            osid1 = binascii.hexlify(f.read(3)).decode()[::-1]
            c = list(osid1)
            c[::2], c[1::2] = c[1::2], c[::2]
            osid1 = "".join(c)[1:]

            f.seek(0x242)
            osid2 = binascii.hexlify(f.read(3)).decode()[::-1]
            c = list(osid2)
            c[::2], c[1::2] = c[1::2], c[::2]
            osid2 = "".join(c)[:5]

            f.seek(0x245)
            osid3 = binascii.hexlify(f.read(3)).decode()[::-1]
            c = list(osid3)
            c[::2], c[1::2] = c[1::2], c[::2]
            osid3 = "".join(c)[1:]

        if uext == "10":
            esid1 = esid2 = esid3 = esid4 = esid5 = esid6 = "00000"
            offsets = [0x240, 0x242, 0x245, 0x230, 0x232, 0x235]
            vars_ = [esid1, esid2, esid3, esid4, esid5, esid6]
            for i in range(6):
                f.seek(offsets[i])
                val = binascii.hexlify(f.read(3)).decode()[::-1]
                c = list(val)
                c[::2], c[1::2] = c[1::2], c[::2]
                val = "".join(c)
                val = val[1:] if i in [0, 2, 3, 5] else val[:5]
                vars_[i] = val
            esid1, esid2, esid3, esid4, esid5, esid6 = vars_

        f.seek(0x248)
        c = list(binascii.hexlify(f.read(6)).decode())
        fsaccess = ["#"] * 21
        for i in range(6):
            val = int(c[i], 16)
            for j in range(4):
                if val & (1 << j):
                    fsaccess[i * 4 + j] = "-"

        f.seek(0x250)
        svcacc = []
        for i in range(32):
            r = f.read(8).rstrip(b"\0")
            svcacc.append(r.decode(errors="ignore"))

        f.seek(0x394)
        b = bin(int(binascii.hexlify(f.read(1)).decode(), 16))[2:].zfill(9)[::-1]
        accesslist = ["true " if b[i] == "1" else "false" for i in range(9)]

        kr = 0
        f.seek(0x39C)
        b = str(int(binascii.hexlify(f.read(1)).decode(), 16))
        if b != "255":
            kmin = b
            kr = 1
        f.seek(0x39D)
        b = str(int(binascii.hexlify(f.read(1)).decode(), 16))
        if b != "255":
            kmaj = "0" + b

        with open(args.rsf[0], "r+b") as f:
            f.seek(0x28)
            s = "\"" + title.rstrip("0") + "\" "
            f.write(s.encode())

            f.seek(0x52)
            f.write(ccode.encode())

            f.seek(0x73)
            s = "\"" + pcode.rstrip("0") + "\""
            f.write(s.encode())

            f.seek(0x16D)
            f.write(uid.encode())

            if uext == "00":
                f.seek(0x4B5)
                f.write(b"E")
                f.seek(0x4C6)
                f.write(exts.encode())
                f.seek(0x4EF)
                f.write(ssid1.encode())
                f.seek(0x50E)
                f.write(ssid2.encode())
                f.seek(0x534)
                f.write(osid1.encode())
                f.seek(0x555)
                f.write(osid2.encode())
                f.seek(0x576)
                f.write(osid3.encode())

            if uext == "10":
                f.seek(0x96C)
                f.write(b"True ")
                f.seek(0x10C9)
                f.write(b"A")
                for offset, val in zip(
                    [0x10E4, 0x10F2, 0x1100, 0x110E, 0x111C, 0x112A],
                    [esid1, esid2, esid3, esid4, esid5, esid6]):
                    if val != "00000":
                        f.seek(offset)
                        f.write(("- 0x" + val).encode())
            # CODE BLOCK FOR FileSystemAccess
            f.seek(0x595) # File System Access
            f.write(fsaccess[0].encode())
            f.seek(0x5B5)
            f.write(fsaccess[1].encode())
            f.seek(0x5D1)
            f.write(fsaccess[2].encode())
            f.seek(0x5EE)
            f.write(fsaccess[3].encode())
            f.seek(0x5FA)
            f.write(fsaccess[4].encode())
            f.seek(0x60E)
            f.write(fsaccess[5].encode())
            f.seek(0x620)
            f.write(fsaccess[6].encode())
            f.seek(0x62B)
            f.write(fsaccess[7].encode())
            f.seek(0x63C)
            f.write(fsaccess[8].encode())
            f.seek(0x647)
            f.write(fsaccess[9].encode())
            f.seek(0x657)
            f.write(fsaccess[10].encode())
            f.seek(0x667)
            f.write(fsaccess[11].encode())
            f.seek(0x67C)
            f.write(fsaccess[12].encode())
            f.seek(0x699)
            f.write(fsaccess[13].encode())
            f.seek(0x6A9)
            f.write(fsaccess[14].encode())
            f.seek(0x6BF)
            f.write(fsaccess[15].encode())
            f.seek(0x6D5)
            f.write(fsaccess[16].encode())
            f.seek(0x6E9)
            f.write(fsaccess[17].encode())
            f.seek(0x6FC)
            f.write(fsaccess[18].encode())
            f.seek(0x707)
            f.write(fsaccess[19].encode())
            f.seek(0x713)
            f.write(fsaccess[20].encode())
            # Ends here
            if kr == 1:
                if args.spoof:
                    f.seek(0x9C7)
                    f.write(b"R")
                    f.seek(0x9E8)
                    f.write(b"02")
                    f.seek(0x9EF)
                    f.write(b"R")
                    f.seek(0xA10)
                    f.write(b"33")
                    print("[SPOOF] Applied")
                else:
                    f.seek(0x9C7)
                    f.write(b"R")
                    f.seek(0x9E8)
                    f.write(kmaj.encode())
                    f.seek(0x9EF)
                    f.write(b"R")
                    f.seek(0xA10)
                    f.write(kmin.encode())
                    print("[SPOOF] Not applied")

            f.seek(0x1168)
            for i in range(32):
                if svcacc[i]:
                    s = "- " + svcacc[i] + " "
                    entry = s.ljust(11, "#")
                    f.write(entry.encode())
                    f.seek(5, 1)

            f.seek(0x13A2)
            f.write(rver.encode())
            f.seek(0x13B7)
            f.write(stack.encode())

            f.seek(0x13D5)
            for d in dep:
                if d != "0000000000000000":
                    f.write(("a: 0x" + d + "L").encode())
                    f.seek(6, 1)

            if args.regionfree:
                with open(args.regionfree[0], "r+b") as rf:
                    rf.seek(8216)
                    rf.write(b"\x7F\xFF\xFF\xFF")
                    print("[REGION FREE] Applied.")