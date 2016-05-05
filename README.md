# keysend

Compress, encrypt, and send files easily using keybase and slack.

The process consists of compression a list of file names with tar and xz. Then the compressed files are encrypted using keybase for a specific user. This encrypted file is then passed up to slack.

## Getting Started

Install the dependencies:

```shell
pip install -r requirements.txt
```

Get a slack API token and set it in a secret environmental variable

```shell
export SLACK_API_TOKEN=xxx000000sssss
```

## Usage

To send some files:

```shell
python keysend.py tmd secrets/*
```
