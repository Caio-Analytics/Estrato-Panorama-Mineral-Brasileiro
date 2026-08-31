-- aggregated per side first, then joined on substância — row-grain join
-- would drop volume where raw/processed come from different mines/years

with bruta as (
    select substancia_mineral as substancia, sum(valor_venda) as valor_venda_bruta, count(*) as n_bruta
    from {{ ref('fct_producao_bruta') }}
    group by 1
),

beneficiada as (
    select substancia_mineral as substancia, sum(valor_venda) as valor_venda_beneficiada, count(*) as n_beneficiada
    from {{ ref('fct_producao_beneficiada') }}
    group by 1
)

select
    coalesce(bruta.substancia, beneficiada.substancia) as substancia,
    coalesce(valor_venda_bruta, 0)       as valor_venda_bruta,
    coalesce(valor_venda_beneficiada, 0) as valor_venda_beneficiada,
    coalesce(valor_venda_beneficiada, 0) - coalesce(valor_venda_bruta, 0) as valor_agregado,
    case when coalesce(valor_venda_bruta, 0) > 0
         then valor_venda_beneficiada / valor_venda_bruta
         else null
    end as fator_agregacao,
    coalesce(n_bruta, 0)       as n_bruta,
    coalesce(n_beneficiada, 0) as n_beneficiada
from bruta
full outer join beneficiada using (substancia)
order by valor_agregado desc nulls last
