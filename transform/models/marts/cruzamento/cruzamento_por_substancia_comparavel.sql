-- Below this many source records on either side, a value-add ratio is too
-- noisy to publish as a ranking (var, so it's a one-line change if the
-- threshold ever needs tuning: dbt run --vars '{min_records_per_side: 10}').

select *
from {{ ref('cruzamento_por_substancia') }}
where n_bruta >= {{ var('min_records_per_side') }}
  and n_beneficiada >= {{ var('min_records_per_side') }}
order by valor_agregado desc nulls last
