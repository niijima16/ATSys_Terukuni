FROM python:3.12.0-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    netcat-openbsd \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 依存関係ファイルをコピーし、依存関係をインストール
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# マイグレーションを実行するスクリプトをコピー
COPY run.sh /app/run.sh

# スクリプトファイルに実行権限を付与
RUN chmod +x /app/run.sh

# サービスを外部からアクセス可能にするためのポートを公開
EXPOSE 8000

# コンテナ起動時のデフォルトコマンドを設定
CMD ["/app/run.sh"]
