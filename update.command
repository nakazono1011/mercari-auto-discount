#!/bin/bash
set -euo pipefail

# Finder 起動でも brew / pyenv を使えるようにする
export PATH="$HOME/.pyenv/shims:$HOME/.pyenv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

REPO_DIR="$HOME/dev/mercari-auto-discount"
APP_DIR="$REPO_DIR/app"
PYENV_PYTHON="$HOME/.pyenv/versions/3.10.13/bin/python"

cd "$REPO_DIR" || {
  echo "ERROR: リポジトリが見つかりません: $REPO_DIR"
  read -r -p "何かキーを押して終了してください"
  exit 1
}

echo 'バージョンを更新します'
git fetch
git checkout main
git reset --hard origin/main

cd "$APP_DIR" || exit 1

if [ ! -x "$PYENV_PYTHON" ]; then
  echo "ERROR: Python 3.10.13 が見つかりません: $PYENV_PYTHON"
  echo "pyenv install 3.10.13 を実行してください"
  read -r -p "何かキーを押して終了してください"
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo '.venv を作成します'
  "$PYENV_PYTHON" -m venv .venv
fi

echo '依存パッケージを更新します'
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# ChromeDriver は Selenium Manager が管理する（brew の chromedriver は使わない）
echo 'ChromeDriver は Selenium が自動管理します（brew chromedriver はスキップ）'

echo 'バージョン更新が完了しました'
read -r -p '何かキーを押して終了してください'
exit 0
