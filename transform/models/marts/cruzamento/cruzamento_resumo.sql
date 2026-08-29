select
    count(*) filter (where n_bruta > 0)                    as n_substancias_bruta,
    count(*) filter (where n_beneficiada > 0)               as n_substancias_beneficiada,
    count(*) filter (where n_bruta > 0 and n_beneficiada > 0) as n_substancias_ambas,
    (select count(*) from {{ ref('cruzamento_por_substancia_comparavel') }}) as n_substancias_comparaveis,
    {{ var('min_records_per_side') }} as min_registros_por_lado
from {{ ref('cruzamento_por_substancia') }}
