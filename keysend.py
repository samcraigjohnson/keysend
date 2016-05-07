from slacker import Slacker

import os
import sys
import argparse
import fileinput
from zipfile import ZipFile
from subprocess import run, PIPE

DEFAULT_CHANNEL = "#general"

slack = Slacker(os.environ['SLACK_API_TOKEN'])

def remove(filename):
    try:
        os.remove(filename)
    except FileNotFoundError as e:
        pass


def compress(archive, files):
    """ Change compression method to zip and use -j command to
    junk the file paths """
    with ZipFile(archive, mode="x") as z:
        for f in files:
            z.write(f, arcname=os.path.basename(f))
    return archive

#################
# Keybase stuff #
#################

def encrypt_message(keybase_user, text):
    process = run(["keybase", "encrypt", keybase_user, "-m", text],
                   stdout=PIPE)
    return process.stdout

def encrypt_file(keybase_user, in_file, out_file):
    run(["keybase", "encrypt", keybase_user, "-i", in_file, "-o", out_file])


################
# Slack stuff  #
################

def send_message_to_user(message, username):
    room_id = get_direct_message_id(username)
    slack.chat.post_message(
        room_id,
        message,
        as_user=True
    )


def send_file_to_user(filename, username):
    room_id = get_direct_message_id(username)
    upload_file_to_channel(filename, room_id)


def upload_file_to_channel(filename, channel):
    slack.files.upload(filename, channels=channel)


def get_direct_message_id(username):
    user_id = get_user_id(username)
    return get_room_id(user_id)


def get_user_id(username):
    """ TODO: check to see if user exists """
    user = [u for u in slack.users.list().body['members']
            if u['name'] == username.lower()][0]
    return user['id']


def get_room_id(user_id):
    im = [im for im in slack.im.list().body['ims'] if im['user'] == user_id][0]
    return im['id']


if __name__ == "__main__":
    # Handle command line arguments
    parser = argparse.ArgumentParser(
        description="Easily send encrypted files through slack"
    )
    group = parser.add_mutually_exclusive_group()

    # Figure out where to send the file
    group.add_argument("-C", "--channel", help="channel to send file to")
    group.add_argument("-u", "--user", help="user to send file to")

    # Get extra info
    parser.add_argument("keybase_user", help="keybase username for encryption")
    parser.add_argument("-f", "--filename", help="specify output filename")

    args, files = parser.parse_known_args()
    if len(files) == 0:
        raise "No filenames found"

    # Filename
    out_file = "message.zip.enc"
    if args.filename:
        out_file = args.filename

    # Channel
    channel = DEFAULT_CHANNEL
    if args.channel:
        channel = args.channel
    elif args.user:
        channel = get_direct_message_id(args.user)

    compress_name = "message.zip"
    compress(compress_name, files)
    encrypt_file(args.keybase_user, compress_name, out_file)
    upload_file_to_channel(out_file, channel)

    remove(compress_name)
    remove(out_file)
