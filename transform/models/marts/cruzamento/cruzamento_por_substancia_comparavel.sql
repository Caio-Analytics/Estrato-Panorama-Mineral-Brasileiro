select *
from {{ ref('cruzamento_por_substancia') }}
where n_bruta >= {{ var('min_records_per_side') }}
  and n_beneficiada >= {{ var('min_records_per_side') }}
order by valor_agregado desc nulls last
