-- Typed, cleaned, snake_case Produção Beneficiada. Unlike Bruta, each
-- quantity here carries its OWN unit (t / kg / ct, varying row to row —
-- a diamond in carats next to bauxite in tonnes), so the unit columns are
-- kept alongside every quantity and nothing downstream sums raw quantities
-- across rows. Only the R$ columns (unit-agnostic) are safe to aggregate —
-- see marts/beneficiada/*.sql.

with source as (
    select * from {{ source('bronze', 'producao_beneficiada') }}
)

select
    _row_id,
    cast("Ano base" as smallint)               as ano_base,
    "UF"                                        as uf,
    "Classe Substância"                         as classe_substancia,
    "Substância Mineral"                        as substancia_mineral,

    {{ parse_br_decimal('"Quantidade Produção"') }}                    as qtd_producao,
    "Unidade de Medida - Produção"              as unidade_producao,
    {{ parse_br_decimal('"Quantidade Contido"') }}                     as qtd_contido,
    nullif("Unidade de Medida - Contido", '-')  as unidade_medida_contido,
    "Indicação Contido"                         as indicacao_contido,

    {{ parse_br_decimal('"Quantidade Venda"') }}                                                          as qtd_venda,
    "Unidade de Medida - Venda"                                                                            as unidade_venda,
    {{ parse_br_decimal('"Valor Venda (R$)"') }}                                                           as valor_venda,
    {{ parse_br_decimal('"Quantidade Consumo/Utilização na Usina"') }}                                     as qtd_transformacao,
    "Unidade de Medida - Consumo/Utilização na Usina"                                                      as unidade_transformacao,
    {{ parse_br_decimal('"Valor Consumo / Utilização na Usina (R$)"') }}                                   as valor_transformacao,
    {{ parse_br_decimal('"Quantidade Transferência para Transformação / Utilização / Consumo"') }}         as qtd_transferencia,
    "Unidade de Medida - Transferência para Transformação / Utilização / Consumo"                          as unidade_transferencia,
    {{ parse_br_decimal('"Valor Transferência para Transformação / Utilização / Consumo (R$)"') }}         as valor_transferencia
from source
