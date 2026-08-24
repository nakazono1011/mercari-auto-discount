#!/bin/bash

cd ~/dev/mercari-auto-discount/app || exit 1

if [ ! -x .venv/bin/python ]; then
  echo "ERROR: .venv がありません。次を実行してください:"
  echo "  cd ~/dev/mercari-auto-discount/app"
  echo "  ~/.pyenv/versions/3.10.13/bin/python -m venv .venv"
  echo "  .venv/bin/pip install -r requirements.txt"
  read -r -p "何かキーを押して終了してください"
  exit 1
fi

exec .venv/bin/python main.py --mode weekly_comment_create
