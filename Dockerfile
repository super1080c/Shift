# Pythonの公式イメージを使う
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /code

# pipをアップグレード
RUN pip install --upgrade pip

# 必要なライブラリをインストール
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# プロジェクトのファイルをコンテナにコピー
COPY . /code/