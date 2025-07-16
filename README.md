# rsfgen-py3
**rsfgen-py3** is a Python 3-compatible version of [rsfgen](https://github.com/ihaveamac/3DS-rom-tools/blob/master/rsfgen/rsfgen.py) by ihaveamac, used to generate `.rsf` files for building or modifying 3DS titles with different configurations

This tool helps extract metadata from a 3DS ROM and a decrypted `exheader.bin`, and writes it into a template RSF file to be used with tools like `makerom`

---

## Features

- Compatible with Python 3.x
- Automatically extracts:
  - Title ID, Product Code, Company Code
  - Stack size, dependencies, access control info
  - Extended Save Data info
- Optionally applies:
  - Region-free patch (to `icon.bin`)
  - Firmware spoofing (to RSF template)

---

## Arguments
|Short|Long|Description|
| --- | --- | --- |
| -r | --rom | Path to a .3ds or .cci rom |
| -e | --exheader | Path to a decrypted `exheader.bin` file |
| -o | --rsf | Path to the RSF template to be used |
| -f | --regionfree | *(Optional)* Path to an `icon.bin` to apply region-free patch |
| -s | --spoof | *(Optional)* Apply firmware spoofing |

---

## Usage
To use this tool, you'll need a decrypted `exheader.bin file`. You can extract it from your .3ds or .cci ROM using [ctrtool](https://github.com/3DSGuy/Project_CTR?tab=readme-ov-file).

Open a terminal in the folder where your ROM is located and run this command:
```
ctrtool --exheader=exheader.bin YourRomName.cci
```
Make sure ctrtool is in your system path or in the same directory as your ROM
<br>
<br>
## Basic Command
(If using the .py, otherwise, if using the .exe just start the command with `rsfgenpy3`)
```
python3 rsfgenpy3.py -r YourRomName.cci -e exheader.bin -o YourRSFName.rsf
```
`-r` or `--rom`: Your ROM file <br>
`-e` or `--exheader`: The exheader.bin file you extracted from the ROM <br>
`-o` or `--rsf`: The RSF file to use and overwrite <br>
<br>
## Note
It is recommended to make a copy of the provided dummy.rsf file and use that copy as the output file. This way, your original template remains unchanged and you won't have to re-download it every time.

<br>

# Credits
- [ihaveamac](https://github.com/ihaveamac)
- Special thanks to my friend [xToxicLynx](https://github.com/xToxicLynx) for the initial conversion and guidance
