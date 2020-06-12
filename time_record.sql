/*
  Copyright (C) 2020 Kondo Taiki

  This file is part of "pg_ssb_run".

  "pg_ssb_run" is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  "pg_ssb_run" is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with "pg_ssb_run".  If not, see <http://www.gnu.org/licenses/>.
*/

-- This table is for recording elapse time each queries.

drop table if exists time_record cascade;

create table time_record (
  global_start text        not null,
  client_no    integer     not null,
  loop_count   integer     not null,
  query_no     text        not null,
  start_time   timestamptz not null,
  end_time     timestamptz,
  result       jsonb,
  PRIMARY KEY (global_start, client_no, loop_count, query_no)
);


