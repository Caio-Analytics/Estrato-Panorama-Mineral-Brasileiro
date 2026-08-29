-- Destination mix by physical quantity (tonnes) — valid here because
-- Bruta's quantities are uniformly tonnes. Contrast with Beneficiada's
-- version, which mixes by value instead.

with base as (
    select
        ano_base,
        sum(qtd_venda_t)         as venda,
        sum(qtd_transformacao_t) as transformacao,
        sum(qtd_transferencia_t) as transferencia
    from {{ ref('fct_producao_bruta') }}
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
