#!/usr/bin/env bash

if [ -d "venv" ]; then
  printf "amoma"
  exit 0
fi

python3 -m venv venv
source ./venv/bin/activate
pip install -r ./requirements.txt
