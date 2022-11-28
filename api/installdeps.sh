#/bin/sh
export TMPDIR=/home/blast/tmp/python
mkdir -p $TMPDIR
/usr/bin/python3 -m venv .venv
source .venv/bin/activate; pip3 install wheel
source .venv/bin/activate; pip3 install -r requirements.txt
source .venv/bin/activate; spacy download it_core_news_lg

rm -rf $TMPDIR/*
