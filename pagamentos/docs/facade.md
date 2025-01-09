# Módulo Pagamentos

## create_contexto_meses_pagamento() -> dict:
	Cria um contexto contendo os nomes dos últimos seis meses no formato
	'Mês/Ano' (ex.: 'Janeiro/2024').
	A função utiliza a configuração de localidade brasileira (pt_BR.UTF-8)
	para formatar os meses corretamente.

* ### Detalhes
    Returns:
        dict: Um dicionário com uma chave "meses", cujo valor é uma lista
        de strings representando os últimos seis meses no formato 'Mês/Ano',
        em ordem decrescente.

* ### Exemplos
        >>> create_contexto_meses_pagamento()
        {'meses': ['Janeiro/2024', 'Dezembro/2023', 'Novembro/2023', ...]}
