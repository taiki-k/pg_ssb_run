\COPY customer FROM 'customer.tbl' WITH (FORMAT csv, DELIMITER '|');
\COPY date FROM 'date.tbl' WITH (FORMAT csv, DELIMITER '|');
\COPY lineorder FROM 'lineorder.tbl' WITH (FORMAT csv, DELIMITER '|');
\COPY part FROM 'part.tbl' WITH (FORMAT csv, DELIMITER '|');
\COPY supplier FROM 'supplier.tbl' WITH (FORMAT csv, DELIMITER '|');

