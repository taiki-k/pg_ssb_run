# pg_ssb_run

Star Schema Benchmarkをいろいろな条件でPostgreSQL上で走らせるためのスクリプト

## はじめに

このスクリプトはStar Schema Benchmark (以下、SSB) をいろいろな条件でPostgreSQL上で走らせるためのスクリプトです。  
ただし、クエリを自由に変えられるので、SSBに限りません。

### ライセンス

GPLv3

## 使い方

### 前提条件

* Python 3系
* Psycopg2(-binary)

### 使用方法

virtualenv での使用を推奨します。

```bash
python pg_ssb_run.py
```

`pg_ssb_run.py` にあるサブディレクトリ `Queries` の中の `*.sql` をすべて実行し、  
すべて実行し終わった段階を 1周 とします。
