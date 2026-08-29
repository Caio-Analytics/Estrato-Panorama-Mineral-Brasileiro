-- Silver-equivalent fact table: stg_producao_bruta + Região + derived
-- value/quality columns. Quantities are uniformly tonnes here, so a
-- physical-quantity total (qtd_total_destinada) is meaningful — contrast
-- with fct_producao_beneficiada, which has no such column.

with stg as (
    select * from {{ ref('stg_producao_bruta') }}
),

regiao as (
    select * from {{ ref('uf_regiao') }}
)

select
    stg.*,
    regiao.regiao,

    stg.valor_venda + stg.valor_transformacao + stg.valor_transferencia as valor_total,
    case when (stg.valor_venda + stg.valor_transformacao + stg.valor_transferencia) > 0
         then stg.valor_venda / (stg.valor_venda + stg.valor_transformacao + stg.valor_transferencia)
         else null
    end as pct_valor_venda,

    stg.qtd_venda_t + stg.qtd_transformacao_t + stg.qtd_transferencia_t as qtd_total_destinada,

    stg.qtd_producao_rom_t <= 0 as flag_producao_zero,
    stg.unidade_medida_contido is not null as flag_possui_teor_contido,
    (stg.qtd_venda_t + stg.qtd_transformacao_t + stg.qtd_transferencia_t)
        > stg.qtd_producao_rom_t * 1.01 as flag_destinacao_excede_producao
from stg
left join regiao on stg.uf = regiao.uf
