with base as (
    select classe_substancia as classe, sum(valor_venda) as valor_venda, count(*) as n_registros
    from {{ ref('fct_producao_beneficiada') }}
    group by 1
),

totals as (
    select sum(valor_venda) as total from base
)

select
    base.classe,
    base.valor_venda,
    base.n_registros,
    base.valor_venda / nullif(totals.total, 0) as pct_valor_nacional
from base
cross join totals
order by base.valor_venda desc
