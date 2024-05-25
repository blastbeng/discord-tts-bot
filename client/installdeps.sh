#/bin/sh
export TMPDIR=/home/blast/tmp
mkdir -p $TMPDIR
/home/blast/.pyenv/versions/3.10.13/bin/python3 -m venv .venv
source .venv/bin/activate; pip3 install -r requirements.txt

rm -rf $TMPDIR/*
