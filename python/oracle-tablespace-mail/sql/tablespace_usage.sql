SELECT
    m.tablespace_name,
    t.contents,
    t.status,
    ROUND(m.used_percent, 2) AS used_percent,
    ROUND(m.used_space * t.block_size / 1024 / 1024, 1) AS used_mb,
    ROUND(m.tablespace_size * t.block_size / 1024 / 1024, 1) AS max_mb
FROM
    dba_tablespace_usage_metrics m
    JOIN dba_tablespaces t
      ON t.tablespace_name = m.tablespace_name
ORDER BY
    m.used_percent DESC,
    m.tablespace_name
