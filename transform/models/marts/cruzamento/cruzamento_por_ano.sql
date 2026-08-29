with b as (
    select ano_base as ano, sum(valor_venda) as valor_venda_bruta
    from {{ ref('fct_producao_bruta') }}
    group by 1
),

f as (
    select ano_base as ano, sum(valor_venda) as valor_venda_beneficiada
    from {{ ref('fct_producao_beneficiada') }}
    group by 1
)

select
    coalesce(b.ano, f.ano)                as ano,
    coalesce(valor_venda_bruta, 0)        as valor_venda_bruta,
    coalesce(valor_venda_beneficiada, 0)  as valor_venda_beneficiada
from b
full outer join f using (ano)
order by ano
