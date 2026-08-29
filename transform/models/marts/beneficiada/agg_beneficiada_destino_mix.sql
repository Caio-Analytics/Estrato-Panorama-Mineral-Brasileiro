-- Destination mix by VALUE (R$), not quantity — Beneficiada's quantities
-- aren't in a uniform unit (t/kg/ct vary by row), so summing them would be
-- invalid. Value is unit-agnostic and is the only safe common denominator.

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
