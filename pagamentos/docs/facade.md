# Módulo Pagamentos

## create_contexto_meses_pagamento() -> dict:
	Cria um contexto contendo os nomes dos últimos seis meses no formato 'Mês/Ano'
    (ex.: 'Janeiro/2024').
	A função utiliza a configuração de localidade brasileira (pt_BR.UTF-8) para for-
    matar os meses corretamente.

* ### Detalhes
    Returns:
        dict: Um dicionário com uma chave "meses", cujo valor é uma lista de strings
        representando os últimos seis meses no formato 'Mês/Ano', em ordem decrescente.

* ### Exemplos
        >>> create_contexto_meses_pagamento()
        {'meses': ['Janeiro/2024', 'Dezembro/2023', 'Novembro/2023', ...]}



### Função: `gerar_cartao_de_ponto_do_colaborador`

Gera os cartões de ponto de um colaborador para um determinado mês e ano,
incluindo informações sobre dias úteis, finais de semana, feriados e status de
admissão ou demissão.

#### Parâmetros
- `colaborador` (`Colaborador`): Instância do colaborador contendo os dados
  pessoais, profissionais e salariais.
- `mes` (`int`): Mês para o qual o cartão de ponto será gerado (1 a 12).
- `ano` (`int`): Ano correspondente ao mês especificado.

#### Retorno
- `QuerySet`: Conjunto de objetos `CartaoPonto` criados para o colaborador no
  intervalo do mês e ano especificados.

#### Comportamento
1. Obtém informações do colaborador:
   - ID pessoal.
   - Data de admissão e, se aplicável, de demissão.
   - Vale-transporte.

2. Define os limites do mês (`primeiro_dia` e `ultimo_dia`).

3. Verifica se cada dia do mês é:
   - Um final de semana.
   - Um feriado (com base em `DiasFeriados`).
   - Anterior à data de admissão ou posterior à data de demissão.

4. Gera um registro de ponto com:
   - Horário padrão de entrada e saída: `"07:00"` e `"17:00"`.
   - Status de remuneração e condução (vale-transporte).
   - Informação de ausência (feriado, final de semana, etc.).

5. Cria os registros em massa no banco de dados com `bulk_create`.

6. Retorna os registros de ponto criados para o intervalo especificado.

#### Exceções
- Certifique-se de que o colaborador possui os dados necessários (`id_pessoal`,
  `data_admissao`, etc.).
- A funcionalidade depende de `DiasFeriados` e de métodos auxiliares como
  `primeiro_e_ultimo_dia_do_mes`.

#### Exemplo de Uso
```python
cartoes = gerar_cartao_de_ponto_do_colaborador(colaborador, 1, 2025)
for cartao in cartoes:
    print(cartao.Dia, cartao.Ausencia, cartao.Remunerado)
