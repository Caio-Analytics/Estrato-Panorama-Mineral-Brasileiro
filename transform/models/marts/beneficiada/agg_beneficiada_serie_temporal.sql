with base as (
    select
        ano_base,
        sum(valor_venda)         as valor_venda,
        sum(valor_transformacao) as valor_transformacao,
        sum(valor_transferencia) as valor_transferencia,
        count(*)                 as n_registros
    from {{ ref('fct_producao_beneficiada') }}
    group by 1
)

select
    *,
    (valor_venda - lag(valor_venda) over (order by ano_base))
        / nullif(lag(valor_venda) over (order by ano_base), 0) as crescimento_valor_venda_yoy
from base
order by ano_base
