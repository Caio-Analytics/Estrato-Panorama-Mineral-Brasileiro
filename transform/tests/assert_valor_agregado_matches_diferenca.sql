select *
from {{ ref('cruzamento_por_substancia') }}
where abs(valor_agregado - (valor_venda_beneficiada - valor_venda_bruta)) > 0.01
