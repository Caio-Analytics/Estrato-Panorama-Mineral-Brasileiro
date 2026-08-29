-- Singular test: fails (returns rows) if valor_agregado ever drifts from
-- its own definition (valor_venda_beneficiada - valor_venda_bruta). A dbt
-- test passes when the query returns zero rows.

select *
from {{ ref('cruzamento_por_substancia') }}
where abs(valor_agregado - (valor_venda_beneficiada - valor_venda_bruta)) > 0.01
