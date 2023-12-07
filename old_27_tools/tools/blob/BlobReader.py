from __future__ import unicode_literals
import os
import steam
import zlib
import sys

def process_file(inputfile, outputdir):
    try:
        print "Processing {}...".format(inputfile)
        with open(inputfile, "rb") as f:
            blob = f.read()

        if blob[0:2] == "\x01\x43":
            blob = zlib.decompress(blob[20:])

        blob2 = steam.blob_unserialize(blob)
        blob3 = steam.blob_dump(blob2)

        output_filename = os.path.splitext(os.path.basename(inputfile))[0] + ".py"
        output_path = os.path.join(outputdir, output_filename)

        with open(output_path, "w") as g:
            g.write("blob = ")
            g.write(blob3)

        print "Written {}".format(output_path)
        print
    except IOError:
        print "Error processing file: {}".format(inputfile)

def process_directory():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(current_dir):
        if filename.endswith(".bin"):
            inputfile = os.path.join(current_dir, filename)
            process_file(inputfile, output_dir)

if __name__ == "__main__":
    print
    print "Steam Server Emulator CDR Reader v1.1"
    print "====================================="
    print
    print "Credits to: pmein1, Dormine"
    print
    print

    process_directory()
