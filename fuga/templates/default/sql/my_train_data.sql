select
    insight_id
    , user_id
    {{ '{% for i in range(14) %}' }}
      , rand() as feature_{{ '{{' }} i {{ '}}' }}
    {{ '{% endfor %}' }}

from
    `repro-1135.repro_io.clips_partitioned`
where
    started_at between
        timestamp(parse_date('%Y-%m-%d', '{{ '{{' }} macros.ds_add(ds, -1) {{ '}}' }}'))
        and timestamp(parse_date('%Y-%m-%d', '{{ '{{' }} ds {{ '}}' }}'))
    and insight_id in (5702, 5706)
