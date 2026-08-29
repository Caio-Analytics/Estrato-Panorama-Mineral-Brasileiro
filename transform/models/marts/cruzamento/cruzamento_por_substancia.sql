-- Bruta x Beneficiada joined by substância — the headline cross-dataset
-- analysis. Aggregated first, then FULL OUTER JOINed on substância rather
-- than joined at row grain: raw and processed output for the same
-- substance don't necessarily come from the same mine in the same year, so
-- a row-grain join would silently drop real volume. Value (R$), never
-- quantity — Beneficiada's units aren't comparable to Bruta's tonnes.

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
