# investimentos.py

def calculate_return_on_investment(initial_value, final_value):
   """
   Calcula o retorno de investimento.

   Args:
       initial_value (float): Valor inicial do investimento.
       final_value (float): Valor final do investimento.

   Returns:
       float: Retorno do investimento em porcentagem.
   """
   reponse = (final_value - initial_value) / initial_value * 100
   return reponse

def calculate_compound_interest(principal, annual_interest_rate, periods):
   """
   Calcula o valor final de um investimento com juros compostos.

   Args:
       principal (float): Valor inicial investido.
       annual_interest_rate (float): Taxa de juros anual em porcentagem.
       periods (int): Número de períodos (anos).

   Returns:
       float: Valor final após o período com juros compostos.
   """
   decimal_interest_rate = annual_interest_rate / 100
   final_value = principal * (1 + decimal_interest_rate) ** periods
   return final_value

def convert_annual_rate_to_monthly(annual_rate):
   """
   Converte uma taxa de juros anual para mensal.

   Args:
       annual_rate (float): Taxa de juros anual em porcentagem.

   Returns:
       float: Taxa de juros mensal em porcentagem.
   """
   monthly_rate = (1 + annual_rate / 100) ** (1 / 12) - 1
   return monthly_rate * 100

def calculate_cagr(initial_value, final_value, years):
   """
   Calcula a taxa de crescimento anual composta (CAGR).

   Args:
       initial_value (float): Valor inicial do investimento.
       final_value (float): Valor final do investimento.
       years (int): Número de anos.

   Returns:
       float: CAGR em porcentagem.
   """
   cagr = ((final_value / initial_value) ** (1 / years) - 1) * 100
   return cagr
