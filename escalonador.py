from tcb import TCB

# Algoritmo FIFO (First-Come, First-Served)
def criterio_de_ordenacao_fifo(tarefa: TCB) -> tuple[int, int]:
    # Retorna uma tupla para ordenar: primeiro pelo tempo de ingresso, depois pelo ID
    return (tarefa.tempo_ingresso, tarefa.id)

def escalonador_fifo(tarefas_prontas: list[TCB], tarefa_atual: TCB | None) -> TCB | None:
    if not tarefas_prontas:
        return None
    
    # Ordena a lista de prontos para garantir a ordem de chegada
    tarefas_prontas.sort(key=criterio_de_ordenacao_fifo)
    
    # O primeiro da lista ordenada é o escolhido
    return tarefas_prontas[0]


# Algoritmo SRTF (Shortest Remaining Time First) 
def escalonador_srtf(tarefas_prontas: list[TCB], tarefa_atual: TCB | None) -> TCB | None:
    if not tarefas_prontas:
        return None

    # Assume a primeira tarefa como a melhor candidata inicial
    melhor_tarefa = tarefas_prontas[0]

    # Percorre o resto da lista para encontrar uma candidata melhor
    for tarefa_candidata in tarefas_prontas[1:]:
        
        # Critério 1: Menor tempo restante.
        # ADICIONADO () AQUI
        if tarefa_candidata.tempo_restante() < melhor_tarefa.tempo_restante():
            melhor_tarefa = tarefa_candidata
            
        # se o tempo restante for igual
        # ADICIONADO () AQUI
        elif tarefa_candidata.tempo_restante() == melhor_tarefa.tempo_restante():
            # Critério 2: Menor tempo de ingresso
            if tarefa_candidata.tempo_ingresso < melhor_tarefa.tempo_ingresso:
                melhor_tarefa = tarefa_candidata

            # se o tempo de ingresso também for igual)
            elif tarefa_candidata.tempo_ingresso == melhor_tarefa.tempo_ingresso:
                # Critério 3: Menor ID
                if tarefa_candidata.id < melhor_tarefa.id:
                    melhor_tarefa = tarefa_candidata

    # Retorna a melhor tarefa encontrada após a verificação
    return melhor_tarefa

# Algoritmo de Prioridade Preemptivo 
def escalonador_prioridade(tarefas_prontas: list[TCB], tarefa_atual: TCB | None) -> TCB | None:
    if not tarefas_prontas:
        return None

    # Assume a primeira tarefa como a de maior prioridade inicial
    melhor_tarefa = tarefas_prontas[0]

    # Percorre o resto da lista para encontrar uma candidata melhor
    for tarefa_candidata in tarefas_prontas[1:]:

        # Critério 1: Maior prioridade.
        if tarefa_candidata.prioridade > melhor_tarefa.prioridade:
            melhor_tarefa = tarefa_candidata

        # se a prioridade for igual
        elif tarefa_candidata.prioridade == melhor_tarefa.prioridade:
            # Critério 2: Menor tempo de ingresso 
            if tarefa_candidata.tempo_ingresso < melhor_tarefa.tempo_ingresso:
                melhor_tarefa = tarefa_candidata
            
            # se o tempo de ingresso também for igual
            elif tarefa_candidata.tempo_ingresso == melhor_tarefa.tempo_ingresso:
                # Critério 3: Menor ID
                if tarefa_candidata.id < melhor_tarefa.id:
                    melhor_tarefa = tarefa_candidata

    # Retorna a tarefa com a maior prioridade 
    return melhor_tarefa

# REGISTRO DE ALGORITMOS 
# Dicionário que mapeia nomes de algoritmos para as funções
ALGORITMOS_REGISTRADOS = {
    'FIFO': escalonador_fifo,
    'SRTF': escalonador_srtf,
    'PRIOP': escalonador_prioridade,
}

def get_escalonador_nome(nome_algoritmo: str):
    """
    Retorna a função de escalonamento real com base no nome (string).
    """
    funcao = ALGORITMOS_REGISTRADOS.get(nome_algoritmo.upper())
    if not funcao:
        raise ValueError(f"Algoritmo '{nome_algoritmo}' desconhecido.")
    return funcao