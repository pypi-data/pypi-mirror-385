# Meu Investimento

Uma biblioteca Python para cálculos de investimentos criada no curso de pós graduação da FIAP em 2025.

## Instalação

Você pode instalar a biblioteca via pip:

```bash
pip install my_investments
```

## Uso

```python
from investments import calculate_return_on_investment, calculate_compound_interest

initial_value = 1000
final_value = 1500

response = calculate_return_on_investment(initial_value, final_value)
print(f"Retorno do investimento: {response:.2f}%")

final_value_rate = calculate_compound_interest(initial_value, 6, 5)
print(f"Valor final com juros compostos: R${final_value_rate:.2f}")
```
