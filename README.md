# pg_ssb_run

Star Schema Benchmarkをいろいろな条件でPostgreSQL上で走らせるためのスクリプト

## はじめに

このスクリプトはStar Schema Benchmark (以下、SSB) をいろいろな条件でPostgreSQL上で走らせるためのスクリプトです。  
ただし、クエリを自由に変えられるので、SSBに限りません。

### ライセンス

このプログラムには、GPLv3が適用されます。

#### 適用される範囲

上記のライセンスが適用されるのは、以下の範囲です。

* pg_ssb_run.py
* prewarm.sql
* load_data.sql
* time_record.sql

## 使い方

### 前提条件

* Python 3.6以降のv3系
* Psycopg2(-binary)

### 使用方法

```
usage: pg_ssb_run.py [-h] [-c CLIENTS] [-l LOOPS] [-C CONFIG] [-q QUERIES]

optional arguments:
  -h, --help            show this help message and exit
  -c CLIENTS, --clients CLIENTS
                        同時実行するクライアント数 (デフォルト: 1 )
  -l LOOPS, --loops LOOPS
                        1クライアントあたりのループ回数 (デフォルト: 1 )
  -C CONFIG, --config CONFIG
                        設定ファイル (デフォルト: pg_ssb_run.ini )
  -q QUERIES, --queries QUERIES
                        クエリが格納されているディレクトリ (デフォルト: Queries )
```

* virtualenv での使用を推奨します。
* 設定ファイルが必要ですので、必ず作成してください。
  * デフォルトでは実行したディレクトリにある`pg_ssb_run.ini`を読み込みます。
  * iniファイルの仕様は、下記を参照してください。
* 特定のディレクトリの中の `*.sql` をすべて実行し、すべて実行し終わった段階を 1周 とします。
  * ディレクトリのデフォルト値は `pg_ssb_run.py` 実行ディレクトリの直下にある `Queries` サブディレクトリです。

### iniファイルの仕様

セクションは `BENCHMARK` と `RESULT` の2つが定義されています。2つとも記載は必須です。  

`BENCHMARK` と `RESULT` は、ともにPostgreSQLへの接続情報を設定し、  
定義されるエントリは同一です。

すべてのエントリは設定が必須で、そのままPsycopg2に渡されます。

| 名前(キー) | 設定値                                         |
| ---------- | ---------------------------------------------- |
| Server     | PostgreSQLの接続先サーバ名 (IPアドレスでも可)  |
| Port       | PostgreSQLの接続先ポート番号                   |
| Database   | PostgreSQLの接続先データベース名               |
| User       | データベースに接続するためのPostgreSQLユーザ名 |
| Password   | Userで設定したユーザ名に対するパスワード(平文) |

接続先のPostgreSQLデータベースがtrust認証の場合は`Password`の値は事実上使用されませんが、  
設定は必要ですので、任意の文字列を指定してください。

以下は、このiniファイルの設定例です。

```ini
[BENCHMARK]
Server   = localhost
Port     = 5432
Database = ssb_test
User     = postgres
Password = dummy

[RESULT]
Server   = localhost
Port     = 5432
Database = ssb_results
User     = postgres
Password = dummy
```

### 実際にStar Schema Benchmarkを走らせるには

[SSBの実行方法](HOWTO_RUN_SSB.md)をご覧ください。

## 参考文献

* Star Schema Benchmarkは、以下のURLで公開されている文献に詳細が記載されています。  
  https://www.cs.umb.edu/~poneil/StarSchemaB.PDF
  * `Queries.sample`にあるクエリは、このプログラムの利用者の利便のために、  
    この文献の"3.1 Query Definition"に掲載されているものを抜粋したものです。
* このプログラムの動作は、以下のURLで公開されているWebページに記載されているDDLで行っています。  
  https://docs.aws.amazon.com/ja_jp/redshift/latest/dg/tutorial-tuning-tables-create-test-data.html
  * `ddl.sample`にあるDDLは、このプログラムの利用者の利便のために、　　
    このWebページのDDL部分を抜粋したものです。
