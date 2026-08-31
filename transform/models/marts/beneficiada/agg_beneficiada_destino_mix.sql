-- by value, not quantity — units vary by row here (t/kg/ct)

with base as (
    select
        ano_base,
        sum(valor_venda)         as venda,
        sum(valor_transformacao) as transformacao,
        sum(valor_transferencia) as transferencia
    from {{ ref('fct_producao_beneficiada') }}
    group by 1
)

select
    ano_base,
    venda,
    transformacao,
    transferencia,
    venda / nullif(venda + transformacao + transferencia, 0)         as pct_venda,
    transformacao / nullif(venda + transformacao + transferencia, 0) as pct_transformacao,
    transferencia / nullif(venda + transformacao + transferencia, 0) as pct_transferencia
from base
order by ano_base
