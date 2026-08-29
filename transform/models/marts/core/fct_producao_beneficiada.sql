-- Silver-equivalent fact table for Produção Beneficiada. No
-- qtd_total_destinada / flag_destinacao_excede_producao here — those
-- would sum quantities across mixed units (t/kg/ct), which is invalid.
-- Value (R$) is unit-agnostic, so it's the only total computed.

with stg as (
    select * from {{ ref('stg_producao_beneficiada') }}
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

    stg.unidade_medida_contido is not null as flag_possui_teor_contido
from stg
left join regiao on stg.uf = regiao.uf
