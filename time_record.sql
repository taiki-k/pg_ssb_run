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


