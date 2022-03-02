### Copyright 2021 Clayton Cronk
### Original packxxu license:
# XXU Packer
# Copyright 2003 Benjamin Moody
# This program is free software; you can redistribute and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111
# USA.
# 

# This program generates and outputs a standard "xxu" (that is to
# say, either 73u or 8xu) OS upgrade file.
# Notes:
#  - Will not validate (obviously)
#  - Should work with TI-Connect (but be prepared to accept that it
#    may not be)
#  - If you're using Unix, make sure you convert your hex file to DOS
#    format first
#  - You should probably use 32 bytes per record
# 

import sys, datetime

usage = ''.join(["usage: {} [OPTIONS] [HEX-FILE]\n",
"where OPTIONS may include:\n",
"  -c ID        set calculator (link device) ID\n",
"  -q ID        set certificate ID\n",
"  -t {83p|73}  set target calculator (i.e. use presets for the above)\n",
"  -d DATE      set date stamp\n",
"  -v VER       set OS version\n",
"  -s SIZE      set program size (apparently unnecessary)\n",
"  -i SIZE      set `image size' (almost certainly unnecessary)\n",
"  -h VER       set maximum compatible hardware version\n",
"  -o FILE      set output file\n"])

infile = sys.stdin
outfile = sys.stdout

v_major=1
v_minor=0
calc=0x73
certid=4
hardware=0xff
ossize=0
imsize=0
tm=datetime.date.today()

def BCD(x):
    return (((x)/10)*16)+((x)%10)
def RECSIZE(n):
    return 13+(2*(n))

def PUTRHEX(x):
    outfile.write(hex(x)[2:].zfill(2).upper())

# Not necessary for Python conversion
# def putrec(n, a, t, data):
#     pass
# def cmdline(opt, *val, **argv):
#     pass

def main(argc, argv):
    # int mon, day, yearh, yearl;
    # int i;
    # unsigned char c;
    # long fileLen;
    # time_t t;
    global infile
    global outfile

    hdr_data = [
        # // Size doesn't matter
        0x80,0x0f, 0x00,0x00,0x00,0x00,
        # // Certificate ID = 4 for 83+, 2 for 73
        0x80,0x11, 0x00,
        # // Version major (may want to set this really high so all OS's will accept)
        0x80,0x21, 0x00,
        # // Version minor
        0x80,0x31, 0x00,
        # // Hardware compatibility (may want to set this to FF)
        0x80,0xa1, 0x00,
        # // Size doesn't matter here either
        0x80,0x7f, 0x00,0x00,0x00,0x00]

    hdr_size = 6+3+3+3+3+6

    # It doesn't matter what we put here -- it won't validate anyway --
    # and using this data at least eliminates any copyright claims :)

    sig_data = [
        0x02,0x0d,0x40,
        0x03,0x14,0x15,0x92, 0x65,0x35,0x89,0x79,
        0x32,0x38,0x46,0x26, 0x43,0x38,0x32,0x79,
        0x50,0x28,0x84,0x19, 0x71,0x69,0x39,0x93,
        0x75,0x10,0x58,0x20, 0x97,0x49,0x44,0x59,
        0x23,0x07,0x81,0x64, 0x06,0x28,0x62,0x08,
        0x99,0x86,0x28,0x03, 0x48,0x25,0x34,0x21,
        0x17,0x06,0x79,0x82, 0x14,0x80,0x86,0x51,
        0x32,0x82,0x30,0x66, 0x47,0x09,0x38,0x44,

        0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff,
        0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff,
        0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff,
        0xff,0xff,0xff,0xff, 0xff]

    # I have no idea what this means.

    end_str = "   -- CONVERT 2.6 --\r\n\032"

    # Not necessary for Python conversion
    # infile = stdin
    # outfile = stdout

    for i in range(1, fileLen(argc)):
        if argv[i][0] == '-':
            if argv[i][1] == 0:
                infile = sys.stdin
            elif argv[i][2]:
                cmdline(argv[i][1],argv[i]+2, argv)
            else:
                cmdline(argv[i][1],argv[i+1], argv)
                i += 1  # May cause issues with Python not being C
        else:
            try:
                infile=open(argv[i],"rb")
            except FileNotFoundError:
                raise Exception("{}: unable to open hex file {}".format(argv[0],argv[i]))

    hdr_data[2] = (ossize>>24)&0xff
    hdr_data[3] = (ossize>>16)&0xff
    hdr_data[4] = (ossize>>8)&0xff
    hdr_data[5] = (ossize)&0xff

    hdr_data[8] = certid
    hdr_data[11] = v_major
    hdr_data[14] = v_minor
    hdr_data[17] = hardware

    hdr_data[20] = (imsize>>24)&0xff
    hdr_data[21] = (imsize>>16)&0xff
    hdr_data[22] = (imsize>>8)&0xff
    hdr_data[23] = (imsize)&0xff

    infile.seek(-1)
    fileLen = infile.tell()  # Get file size
    infile.seek(0)

    fileLen += RECSIZE(hdr_size) + RECSIZE(0) + 3*RECSIZE(32) + RECSIZE(0) - 2 + len(end_str)

    day = tm.day
    mon = tm.month
    yearh = int(str(tm.year)[0:2])
    yearl = int(str(tm.year)[2:3])

    outfile.write("**TIFL**")

    outfile.write(0)
    outfile.write(0)

    outfile.write("\001\210{}{}{}{}\010basecode".format(BCD(mon), BCD(day), BCD(yearh), BCD(yearl)))

    for i in range(23):
        outfile.write(0);		# A whole bunch of zeroes.

    outfile.write(calc)		# Type of calculator
    outfile.write(0x23)		# "Data type" for OS upgrade

    for i in range(24):
        outfile.write(0)		# And even more zeroes.

    outfile.write(fileLen & 0xff)	# The length of the entire rest of the file
    outfile.write((fileLen >> 8) & 0xff)
    outfile.write((fileLen >> 16) & 0xff)
    outfile.write((fileLen >> 24) & 0xff)

    # OS header
    putrec(hdr_size, 0, 0, hdr_data)
    putrec(0, 0, 1, None)

    # Actual OS data
    for i in range(fileLen):
        c = infile.read(1)
        if c < 128:
            outfile.write(c)
    

    # And a dumb signature
    putrec(32, 0, 0, sig_data)
    putrec(32, 32, 0, sig_data+32)
    putrec(32, 64, 0, sig_data+64)
    putrec(0, 0, -1, None)
    outfile.write(end_str)

    infile.close()
    outfile.close()

    return 0



def putrec(n, a, t, data):
    # // Use t=-1 to get the final record without newline
    c = 0
    outfile.write(':')

    PUTRHEX(n)
    PUTRHEX( (a >> 8) & 0xff)
    PUTRHEX(a & 0xff)
    PUTRHEX(-t if t < 0 else t)

    for i in range(n):
        PUTRHEX(data[i])

    PUTRHEX(256-(c&0xff))

    if t >= 0:
        outfile.write("\r\n")



def cmdline(opt, val, **argv):
    # float foo;
    # int i;

    if opt == 'd':
        if val == '/':
            val = "%d/%d/%d".format(tm.month, tm.day, tm.year)
        else:
            val = "%d%d%d".format(tm.day, tm.month, tm.year)
        if tm.year > 1900:
            tm.year -= 1900     # POTENTIAL BREAKAGE
    elif opt == 'v':
        foo = '{}'.format(val)
        v_major = int(foo)
        v_minor = (int(foo) * 100) % 100
    elif opt == 't':
        if val == '73':
            calc = 0x74
            certid = 2
        elif val == '83p':
            calc = 0x73
            certid = 4
        else:
            raise Exception("{}: unknown calculator type {}. Try '73' or '83p'.".format(argv[0],val))

    elif opt == 'c':
        val = "%x".format(calc)     # POTENTIAL BREAKAGE
    elif opt == 'q':
        val = "%x".format(certid)   # POTENTIAL BREAKAGE
    elif opt == 's':
        val = "%li".format(ossize)  # POTENTIAL BREAKAGE
    elif opt == 'i':
        val = "%li".format(imsize)  # POTENTIAL BREAKAGE
    elif opt == 'h':
        val = "%i".format(hardware) # POTENTIAL BREAKAGE
    elif opt == 'o':
        if val == '-':
            outfile = sys.stdout
        else:
            try:
                outfile = open(val, 'wb')
            except:
                raise Exception("{}: unable to open XXU file {}\n".format(argv[0],val))
                exit(1)
    else:
        raise Exception("{}: unknown option '{}'\n".format(argv[0], opt))
