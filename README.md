# pg_ssb_run

Star Schema Benchmarkをいろいろな条件でPostgreSQL上で走らせるためのスクリプト

## はじめに

このスクリプトはStar Schema Benchmark (以下、SSB) をいろいろな条件でPostgreSQL上で走らせるためのスクリプトです。  
ただし、クエリを自由に変えられるので、SSBに限りません。

### ライセンス

GPLv3

## 使い方

### 前提条件

* Python 3.6移行のv3系
* Psycopg2(-binary)

### 使用方法

```
usage: pg_ssb_run.py [-h] [-c CLIENTS] [-l LOOPS] [-C CONFIG] [-q QUERIES]

optional arguments:
  -h, --help            show this help message and exit
  -c CLIENTS, --clients CLIENTS
                        同時実行するクライアント数
  -l LOOPS, --loops LOOPS
                        1クライアントあたりのループ回数
  -C CONFIG, --config CONFIG
                        設定ファイル
  -q QUERIES, --queries QUERIES
                        クエリが格納されているディレクトリ
```

* virtualenv での使用を推奨します。
* 特定のディレクトリの中の `*.sql` をすべて実行し、すべて実行し終わった段階を 1周 とします。
  * ディレクトリのデフォルト値は `pg_ssb_run.py` 実行ディレクトリの直下にある `Queries` サブディレクトリです。
