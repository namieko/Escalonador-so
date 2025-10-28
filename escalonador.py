from tcb import TCB

# Funções de escalonamento
# Algoritmo FIFO (First-Come, First-Served)
def criterio_de_ordenacao_fifo(tarefa: TCB) -> tuple[int, int]:
    # Ordena primeiro pelo tempo de chegada, depois pelo ID
    return (tarefa.tempo_ingresso, tarefa.id)

def escalonador_fifo(tarefas_prontas: list[TCB], tarefa_atual: TCB | None) -> TCB | None:
    if not tarefas_prontas:
        return None #Fila vazia
    # Ordena a lista de prontos e escolhe a primeira
    tarefas_prontas.sort(key=criterio_de_ordenacao_fifo)
    return tarefas_prontas[0]

# Algoritmo SRTF (Shortest Remaining Time First) 
def escalonador_srtf(tarefas_prontas: list[TCB], tarefa_atual: TCB | None) -> TCB | None:
    if not tarefas_prontas:
        return None

    # Assume a primeira tarefa como a melhor candidata inicial
    melhor_tarefa = tarefas_prontas[0]

    # Percorre o resto da lista para encontrar uma candidata melhor
    for tarefa_candidata in tarefas_prontas[1:]:
        
        # Menor tempo restante
        if tarefa_candidata.tempo_restante() < melhor_tarefa.tempo_restante():
            melhor_tarefa = tarefa_candidata
            
        # se o tempo restante for igual, vê o tempo de ingresso
        elif tarefa_candidata.tempo_restante() == melhor_tarefa.tempo_restante():
            if tarefa_candidata.tempo_ingresso < melhor_tarefa.tempo_ingresso:
                melhor_tarefa = tarefa_candidata

            # se o tempo de ingresso também for igual, vê o ID
            elif tarefa_candidata.tempo_ingresso == melhor_tarefa.tempo_ingresso:
                if tarefa_candidata.id < melhor_tarefa.id:
                    melhor_tarefa = tarefa_candidata

    return melhor_tarefa

# Algoritmo de Prioridade Preemptivo (PRIOP)
def escalonador_prioridade(tarefas_prontas: list[TCB], tarefa_atual: TCB | None) -> TCB | None:
    if not tarefas_prontas:
        return None

    melhor_tarefa = tarefas_prontas[0]

    # Percorre a lista para encontrar uma candidata melhor
    for tarefa_candidata in tarefas_prontas[1:]:

        # Maior prioridade.
        if tarefa_candidata.prioridade > melhor_tarefa.prioridade:
            melhor_tarefa = tarefa_candidata

        # se a prioridade for igual, vê o tempo de ingresso
        elif tarefa_candidata.prioridade == melhor_tarefa.prioridade:
            if tarefa_candidata.tempo_ingresso < melhor_tarefa.tempo_ingresso:
                melhor_tarefa = tarefa_candidata
            
            # se o tempo de ingresso também for igual, vê o ID
            elif tarefa_candidata.tempo_ingresso == melhor_tarefa.tempo_ingresso:
                if tarefa_candidata.id < melhor_tarefa.id:
                    melhor_tarefa = tarefa_candidata

    return melhor_tarefa

# Registro de algoritmos
# Dicionário que mapeia nomes de algoritmos para as funções
ALGORITMOS_REGISTRADOS = {
    'FIFO': escalonador_fifo,
    'SRTF': escalonador_srtf,
    'PRIOP': escalonador_prioridade,
}

def get_escalonador_nome(nome_algoritmo: str):
    """Retorna a função correspondente ao nome do algoritmo."""
    funcao = ALGORITMOS_REGISTRADOS.get(nome_algoritmo.upper())
    if not funcao:
        raise ValueError(f"Algoritmo '{nome_algoritmo}' desconhecido.")
    return funcao