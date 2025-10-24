# carregador.py
from dataclasses import dataclass
from tcb import TCB
from typing import List

@dataclass
class DadosConfiguracao:
    """Uma estrutura de dados para guardar o que foi lido do arquivo."""
    tarefas: List[TCB]
    algoritmo_nome: str
    quantum: int

def carregar_dados_configuracao(caminho_arquivo: str) -> DadosConfiguracao:
    """
    Lê um arquivo de configuração, processa-o e retorna
    uma estrutura de dados com as tarefas e configurações.
    
    Esta função LANÇA EXCEÇÕES se o arquivo for inválido,
    para que a GUI possa capturá-las e mostrar ao usuário.
    """
    lista_de_tcbs: List[TCB] = []
    
    with open(caminho_arquivo, 'r') as f:
        # 1. Processa a primeira linha (Parâmetros do Sistema)
        linha_sistema = f.readline().strip().split(';')
        if len(linha_sistema) < 2:
            raise ValueError("Formato inválido da primeira linha. Esperado: algoritmo;quantum")
        
        algoritmo_str = linha_sistema[0]
        quantum = int(linha_sistema[1])
        
        # 2. Processa as linhas de tarefa
        for linha_texto in f:
            if not linha_texto.strip(): 
                continue # Pula linhas em branco
            
            partes = linha_texto.strip().split(';')
            if len(partes) < 5:
                raise ValueError(f"Linha de tarefa incompleta: '{linha_texto}'")

            novo_tcb = TCB(
                id=int(partes[0]), 
                cor=partes[1], 
                tempo_ingresso=int(partes[2]), 
                duracao_total=int(partes[3]), 
                prioridade=int(partes[4]),
                lista_eventos=partes[5:] if len(partes) > 5 else []
            )
            lista_de_tcbs.append(novo_tcb)

    if not lista_de_tcbs:
        raise ValueError("Nenhuma tarefa válida foi encontrada no arquivo.")

    # 3. Retorna os dados prontos
    return DadosConfiguracao(
        tarefas=lista_de_tcbs,
        algoritmo_nome=algoritmo_str,
        quantum=quantum
    )