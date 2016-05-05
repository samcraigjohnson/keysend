from slacker import Slacker

import os
import sys
import tarfile
from subprocess import call

CHANNEL = "#_test"

slack = Slacker(os.environ['SLACK_API_TOKEN'])

def remove(filename):
    try:
        os.remove(filename)
    except FileNotFoundError as e:
        pass

def compress(filename, files, compression="xz"):
    mode = "x:" + compression
    with tarfile.open(filename, mode=mode) as tar:
        for f in files:
            tar.add(f)

def encrypt_file(keybase_user, in_file, out_file):
    call(["keybase", "encrypt", keybase_user, "-i", in_file, "-o", out_file])

def upload_file(filename, channel=CHANNEL):
    slack.files.upload(filename, channels=channel)


if __name__ == "__main__":
    # Read the command line arguments
    to_user = sys.argv[1]
    in_files = sys.argv[2:]

    # Compress all the files passed in
    compressed_file = "/tmp/message.tar.xz"
    compress(compressed_file, in_files)

    # Encrypt the compressed archive
    out_file = compressed_file + ".enc"
    encrypt_file(to_user, compressed_file, out_file)

    # Send encrypted, compressed file to slack channel
    upload_file(out_file)

    # Cleanup files
    remove(compressed_file)
    remove(out_file)
