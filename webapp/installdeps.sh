#/bin/sh
export TMPDIR=/home/blast/tmp/python
mkdir -p $TMPDIR
/usr/bin/python3 -m venv .venv
source .venv/bin/activate; pip3 install -r requirements.txt

rm -rf $TMPDIR/*
