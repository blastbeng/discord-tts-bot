#/usr/bin/bash
export TMPDIR=/home/blast/tmp/python
mkdir -p $TMPDIR
python3 -m venv .venv
source .venv/bin/activate; pip3 install wheel
source .venv/bin/activate; pip3 install -r requirements.txt
source .venv/bin/activate; spacy download en_core_web_sm
source .venv/bin/activate; spacy download fr_core_news_sm
source .venv/bin/activate; spacy download de_core_news_sm
source .venv/bin/activate; spacy download it_core_news_sm
source .venv/bin/activate; spacy download pt_core_news_sm
source .venv/bin/activate; spacy download es_core_news_sm
rm -rf $TMPDIR/*
