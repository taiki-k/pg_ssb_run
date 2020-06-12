# Star Schema Benchmark の実行方法

## データを投入する

### テーブル作成

1. `ddl.sample`にある`create_table.sql` を用いて、ベンチマーク対象のマシン上のPostgreSQLにテーブルを作成します。
   * `lineorder`テーブルの`lo_orderkey`列は、**SF=300以上の走行を予定している場合は`bigint`にして**ください。  
     SF=300(GB)以上の場合、`integer`の範囲を超えてしまいます。
2. `time_record.sql` を用いて、ベンチマーク結果を格納するマシン上のPostgreSQLにテーブルを作成します。

### データ作成

#### データ生成ツールのビルド

1. データ生成ツール`dbgen`を取得します。  
   [こちらのツール](https://github.com/LucidDB/thirdparty/blob/master/ssb.tar.bz2)で動作確認を行っています。
2. コンパイルが必要ですので、取得したファイルをtarで展開します。
3. 展開したファイルの中にある `makefile` を編集します。  
   17行目を、以下のように変更したうえで、`make`コマンドでビルドしてください。

```diff
--- makefile.or 2019-01-22 22:07:08.751512162 +0900
+++ makefile    2018-12-18 20:54:41.600104826 +0900
@@ -14,7 +14,7 @@
 #
 # add -EDTERABYTE if orderkey will execeed 32 bits (SF >= 300)
 # and make the appropriate change in gen_schema() of runit.sh
-CFLAGS = -O -DDBNAME=\"dss\" -D$(MACHINE) -D$(DATABASE) -D$(WORKLOAD)
+CFLAGS = -O3 -DDBNAME=\"dss\" -D$(MACHINE) -D$(DATABASE) -D$(WORKLOAD) -fstack-protector-all
 LDFLAGS = -O
 # The OBJ,EXE and LIB macros will need to be changed for compilation under
 #  Windows NT
```

#### データ生成

* 付属スクリプト`createdb`でデータを作成します。  
  指定したScale Factorのディレクトリが作成されますが、生成した後でファイルで移動する動作ですので、以下の点にご注意ください。
  * 複数のScale Factorのデータを同時に作成することはできません。  
    **同時に実行した場合、ファイル名が重複するため、データが破損します。**
  * `createdb`を実行するディレクトリのディスク容量にご注意ください。  
    指定したSF分のデータが一時的に作成されます。  
    **容量不足でエラー終了しても、メッセージなどで知らせてくれません。**

##### 使用方法

```
$ ./createdb [SF]
```

選択可能なパラメータ`SF`とデータサイズの関係は、以下の表のとおりです。

| SF      | データサイズ |
| ------- | ------------ |
| 100M    | 100MB        |
| 1G      | 1GB          |
| 10G     | 10GB         |
| 30G     | 30GB         |
| 100G    | 100GB        |
| 300G    | 300GB        |
| 1000G   | 1TB          |
| 3000G   | 3TB          |
| 10000G  | 10TB         |
| 30000G  | 30TB         |
| 100000G | 100TB        |

上記の表にないサイズのデータを生成したい場合は、以下のようにします。(例:データサイズ 70GB)

```
$ scale=70 datasize=70G ./createdb
```

なお、以下の実行例の通り、100Gで1時間強かかりますのでご注意ください。

##### 実行例

```
$ time ./createdb 100G
real    62m55.565s
user    61m12.326s
sys     2m32.665s
$ cd gen/100G
$ ls -lh *.tbl
-rw-rw-r--. 1 kondo kondo 274M  1月  8 20:12 customer.tbl
-rw-rw-r--. 1 kondo kondo 223K  1月  8 20:12 date.tbl
-rw-rw-r--. 1 kondo kondo  59G  1月  8 20:58 lineorder.tbl
-rw-rw-r--. 1 kondo kondo 115M  1月  8 20:58 part.tbl
-rw-rw-r--. 1 kondo kondo  81M  1月  8 20:58 supplier.tbl
```

#### データ投入

* まず、生成したデータを格納するためのデータベースを`createdb`などで作成してください。
* そのデータベースで、pg_prewarmを有効にしてください。  
  `=# CREATE EXTENSION pg_prewarm;`
* `load_data.sql`を使用して、生成したデータをデータベースに格納していきます。
  * PSQLのコマンドを使用していますので、**`psql -f` を使用してください**。
  * カレントディレクトリに生成したデータがあることが前提になっています。  
    **`gen/[SF]` にディレクトリを移ってから**実行してください。

## ベンチマークを実行する

### iniファイルを作成する。

[README.md](/README.md)記載のiniファイルの仕様にしたがって、iniファイルを作成してください。

### Pre-Warm (省略可)

* `prewarm.sql`を使用して、全データの共有バッファ読み出しを試みます。
  * 実行前に、PostgreSQLのGUC `shared_buffers` が適切な値に設定されているかを確認しください。
  * pg_prewarmが有効となっていることが前提ですので、必ず有効にしてください。

### 実行

* [README.md](README.md)の実行方法の記載にしたがって、`pg_ssb_run.py`を実行してください。
  * Star Schema Benchmarkのサンプルクエリは、`Queries.sample`にあります。  
    これを利用する場合は、`-q`オプションでディレクトリを指定してください。

## 結果を確認する

結果は、ベンチマーク結果を格納するマシンのPostgreSQLの、指定したデータベースに格納されています。  
テーブル名は、`time_record`です。
