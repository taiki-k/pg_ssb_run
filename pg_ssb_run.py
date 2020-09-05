#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2020 Kondo Taiki
#
# This file is part of "pg_ssb_run".
#
# "pg_ssb_run" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "pg_ssb_run" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "pg_ssb_run".  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import glob
import argparse
import psycopg2
from psycopg2.extras import Json
import datetime, time
import configparser
import concurrent.futures

def pg_connect(server, port, database, user, password):
  """
  pg_connect -- PostgreSQLに接続する。
  入力値 : 
    server   : 接続先サーバ
    port     : 接続先ポート番号
    database : 接続先データベース名
    user     : 接続ユーザ名
    password : 接続パスワード
  返却値 : 接続されたインスタンス
  """
  dsn = u"postgresql://" + user + ":" + password + "@" + server + ":" + port + "/" + database
  ret = psycopg2.connect(dsn)
  return ret

def runner(benchmark_server, result_server, global_start, sql_files, loop_cnt, client_no):
  """
  runner -- ベンチマークを実行する。
  入力値 :
    benchmark_server : ベンチマークサーバ
    result_server    : 結果格納先サーバ
    global_start     : ベンチマーク開始時刻(ベンチマーク結果の識別ID)
    sql_files        : ベンチマーク対象クエリのファイル名
    loop_cnt         : ループ回数
    client_no        : クライアント番号
  """
  # 結果格納用
  pg_conn_result = pg_connect(result_server['Server'], result_server['Port'], result_server['Database'], result_server['User'], result_server['Password'])
  pg_conn_result.autocommit = True
  # ベンチマーク実施サーバ
  pg_conn_benchmark = pg_connect(benchmark_server['Server'], benchmark_server['Port'], benchmark_server['Database'], benchmark_server['User'], benchmark_server['Password'])

  for i in range(1, loop_cnt + 1):
    print(u"[CLIENT %d] [LOOP %d] Benchmark starts." % (client_no, i))
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
        cur.execute(u"INSERT INTO time_record (global_start, client_no, loop_count, query_no, start_time) VALUES ( %s, %s, %s, %s, now());", (global_start, client_no, i, query_no))

      # クエリ実行
      print(u"[CLIENT %d] [LOOP %d] Start query \"%s\"." % (client_no, i, query_no))
      rows = None
      with pg_conn_benchmark.cursor() as cur:
        # TODO: EXPLAINと非EXPLAINの両方に対応させる
        # EXPLAIN時は、結果はかならず1行1列
        cur.execute(query_text)
        rows = cur.fetchone()
      
      # クエリ実行終了日時の記録
      with pg_conn_result.cursor() as cur:
        # TODO: EXPLAINと非EXPLAINの両方に対応させる
        cur.execute(u"UPDATE time_record SET end_time = now(), result = %s WHERE global_start = %s and client_no = %s and loop_count = %s and query_no = %s;" , (Json(rows[0]), global_start, client_no, i, query_no))

    print(u"[CLIENT %d] [LOOP %d] Benchmark ended." % (client_no, i))

  # ベンチマーク終了
  # 接続をClose
  pg_conn_result.close()
  pg_conn_benchmark.close()

def task(params):
  """
  task -- マルチプロセッシングの呼び出し口
  入力値:
    param: Tuple (
      enchmark_server : ベンチマークサーバ
      result_server    : 結果格納先サーバ
      global_start     : ベンチマーク開始時刻(ベンチマーク結果の識別ID)
      sql_files        : ベンチマーク対象クエリのファイル名
      loop_cnt         : ループ回数
      client_no        : クライアント番号
    )
  """
  (benchmark_server, result_server, global_start, sql_files, loop_count, c_no) = params
  runner(benchmark_server, result_server, global_start, sql_files, loop_count, c_no)

def main(dir, loop_count, client_count, config):
  """
  main -- 全体制御関数
  入力値:
    dir          : クエリが格納されているディレクトリ
    loop_count   : ベンチマーク実行回数
    client_count : 同時実行するクライアント数
    config       : Configファイル名
  """
  # Configファイルの読み込み
  config_ini = configparser.ConfigParser()
  config_ini.read(config, encoding = 'utf-8')

  sql_files = glob.glob(dir + u"/*.sql")

  # ベンチマーク開始時刻(ベンチマーク結果の識別ID)
  global_start = datetime.datetime.now().strftime(u'%Y%m%d_%H%M%S')

  # ベンチマーク対象サーバと結果格納サーバの情報を準備
  benchmark_server = config_ini['BENCHMARK']
  result_server = config_ini['RESULT']

  print(u"Start all of queries in \"%s\" directory." % dir)
  print(u"Benchmark time of each queries will be recorded at \"time_record\" table")
  print(u"with \"global_start\" = %s" % global_start)

  if client_count == 1:
    # シングルクライアント
    print(u"Single Client mode")
    print(u"The client runs %d time(s)." % loop_count)
    runner(benchmark_server, result_server, global_start, sql_files, loop_count, 1)
  else:
    # マルチクライアント
    print(u"Multi Client mode: Number of Client is %d" % client_count)
    print(u"Each clients runs %d time(s)." % loop_count)
    with concurrent.futures.ProcessPoolExecutor(max_workers = client_count) as executor:
      params = map(lambda n : (benchmark_server, result_server, global_start, sql_files, loop_count, n), range(1, client_count + 1))
      executor.map(task, params)


# 最初
if __name__ == "__main__":
  # 引数の格納先とデフォルト値
  num_clients = 1
  num_loops = 1
  config_file = u"pg_ssb_run.ini"
  query_dir = u"Queries"

  # 引数の定義
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument("-c", "--clients", type = int, help = u"同時実行するクライアント数 (デフォルト: " + str(num_clients) + u" )")
  arg_parser.add_argument("-l", "--loops", type = int, help = u"1クライアントあたりのループ回数 (デフォルト: " + str(num_loops) + u" )")
  arg_parser.add_argument("-C", "--config", type = str, help = u"設定ファイル (デフォルト: " + config_file + u" )")
  arg_parser.add_argument("-q", "--queries", type = str, help = u"クエリが格納されているディレクトリ (デフォルト: " + query_dir + u" )")
  args = arg_parser.parse_args()

  # 引数の設定
  if args.clients:
    num_clients = args.clients
  
  if args.loops:
    num_loops = args.loops
  
  if args.config:
    config_file = args.config

  if args.queries:
    query_dir = args.queries  

  main(query_dir, num_loops, num_clients, config_file)
