-- Typed, cleaned, snake_case Produção Bruta — the dbt-native replacement
-- for etl/silver.py's Bruta branch. Every quantity here is in tonnes
-- (baked into the source column names), so summing them downstream is
-- numerically meaningful — see stg_producao_beneficiada.sql for the
-- dataset where that is NOT true.

with source as (
    select * from {{ source('bronze', 'producao_bruta') }}
)

select
    _row_id,
    cast("Ano base" as smallint)               as ano_base,
    "UF"                                        as uf,
    "Classe Substância"                         as classe_substancia,
    "Substância Mineral"                        as substancia_mineral,

    {{ parse_br_decimal('"Quantidade Produção - Minério ROM (t)"') }}  as qtd_producao_rom_t,
    {{ parse_br_decimal('"Quantidade Contido"') }}                     as qtd_contido,
    nullif("Unidade de Medida - Contido", '-')  as unidade_medida_contido,
    "Indicação Contido"                         as indicacao_contido,

    {{ parse_br_decimal('"Quantidade Venda (t)"') }}                                                    as qtd_venda_t,
    {{ parse_br_decimal('"Valor Venda (R$)"') }}                                                         as valor_venda,
    {{ parse_br_decimal('"Quantidade Transformação / Consumo / Utilização (t)"') }}                       as qtd_transformacao_t,
    {{ parse_br_decimal('"Valor Transformação / Consumo / Utilização nesta mina (R$)"') }}                as valor_transformacao,
    {{ parse_br_decimal('"Quantidade Transferência para Transformação / Utilização / Consumo (t)"') }}    as qtd_transferencia_t,
    {{ parse_br_decimal('"Valor Transferência para Transformação / Utilização / Consumo (R$)"') }}        as valor_transferencia
from source
