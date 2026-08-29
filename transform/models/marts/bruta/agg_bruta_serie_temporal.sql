-- Yearly roll-up with window-function YoY growth — the SQL equivalent of
-- the old pandas .pct_change() in etl/gold.py.

with base as (
    select
        ano_base,
        sum(qtd_producao_rom_t) as producao_rom_t,
        sum(valor_venda)        as valor_venda,
        sum(valor_transformacao) as valor_transformacao,
        sum(valor_transferencia) as valor_transferencia,
        count(*)                as n_registros
    from {{ ref('fct_producao_bruta') }}
    group by 1
)

select
    *,
    (valor_venda - lag(valor_venda) over (order by ano_base))
        / nullif(lag(valor_venda) over (order by ano_base), 0) as crescimento_valor_venda_yoy,
    (producao_rom_t - lag(producao_rom_t) over (order by ano_base))
        / nullif(lag(producao_rom_t) over (order by ano_base), 0) as crescimento_producao_yoy
from base
order by ano_base
