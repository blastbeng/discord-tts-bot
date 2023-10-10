#/usr/bin/bash
export TMPDIR=/home/blast/tmp/python
/usr/bin/python3 -m venv .venv
source .venv/bin/activate; pip3 install -r requirements.txt