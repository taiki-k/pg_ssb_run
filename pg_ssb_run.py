#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import glob
import argparse
import psycopg2
from psycopg2.extras import Json
import datetime, time
#import fcntl
import concurrent.futures


# ======================= config =====================
# PostgreSQL
pg_server = u'localhost'
pg_port = u'5432'
pg_database = u'ssb_results'
pg_user = u'postgres'
pg_pass = u'dummy'
# ====================================================

# PostgreSQLに接続する。
# 入力値 : 
#   server   : 接続先サーバ
#   port     : 接続先ポート番号
#   database : 接続先データベース名
#   user     : 接続ユーザ名
#   password : 接続パスワード
# 返却値 : 接続されたインスタンス
def pg_connect(server, port, database, user, password):
  dsn = u"postgresql://" + user + ":" + password + "@" + server + ":" + port + "/" + database
  ret = psycopg2.connect(dsn)
  return ret

# ベンチマークを実行する。
# 入力値 :
#   server   : 接続先サーバ
#   port     : 接続先ポート番号
#   database : 接続先データベース名
#   user     : 接続ユーザ名
#   password : 接続パスワード
#   sql_files: ベンチマーク対象クエリのファイル名
#   loop_cnt : ループ回数
#   client_no: クライアント番号
def runner(server, port, database, user, password, sql_files, loop_cnt, client_no):
  # 結果格納用
  pg_conn_result = pg_connect(pg_server, pg_port, pg_database, pg_user, pg_pass)
  pg_conn_result.autocommit = True
  # ベンチマーク実施サーバ
  pg_conn_benchmark = pg_connect(server, port, database, user, password)

  # ベンチマーク開始時刻(ベンチマーク結果の識別ID)
  global_start = datetime.datetime.now().strftime(u'%Y%m%d_%H%M%S')
  for i in range(1, loop_cnt + 1):
    for sql_file in sql_files:
      # クエリ番号をファイル名から導出
      query_no = os.path.splitext(os.path.basename(sql_file))[0]
      
      # ファイルからクエリを抽出
      query_text = None
      with open(sql_file, "r") as query_data:
        query_text = query_data.read()
        query_data.close()

      # TODO: EXPLAINと非EXPLAINの両方に対応させる
      # if use_explain:
      query_text = u"EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON) \n" + query_text

      # クエリ実行開始日時の記録
      with pg_conn_result.cursor() as cur:
        cur.execute(u"INSERT INTO time_record (global_start, client_no, loop_count, query_no, start_time) VALUES ( %s, %s, %s, %s, now());", (global_start, client_no, loop_cnt, query_no))

      # クエリ実行
      rows = None
      with pg_conn_benchmark.cursor() as cur:
        # TODO: EXPLAINと非EXPLAINの両方に対応させる
        # EXPLAIN時は、結果はかならず1行1列
        cur.execute(query_text)
        rows = cur.fetchone()
      
      # クエリ実行終了日時の記録
      with pg_conn_result.cursor() as cur:
        # TODO: EXPLAINと非EXPLAINの両方に対応させる
        cur.execute(u"UPDATE time_record SET end_time = now(), result = %s WHERE global_start = %s and client_no = %s and loop_count = %s and query_no = %s;" , (Json(rows[0]), global_start, client_no, loop_cnt, query_no))

# main
#    
def main():
  sql_files = glob.glob("Queries/*.sql")

  #TODO: マルチクライアント化
  runner(u"localhost", u"5432", u"ssb_test", pg_user, pg_pass, sql_files, 1, 1)


if __name__ == "__main__":
#  arg_parser = argparse.ArgumentParser()
#  arg_parser.add_argument("-c", "--clients", type = int, help = u"同時実行するクライアント数")
#  args = arg_parser.parse_args()
#  print(args.clients)

  #num_psql_worker = 1 # デフォルト値

  main()
