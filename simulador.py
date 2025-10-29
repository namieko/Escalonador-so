from tcb import TCB
from typing import Callable
from cpu import CPU, EventoCPU  # Importa a CPU e seus eventos.

#Tipo da função escalonadora: recebe lista de TCBs e a tarefa atual; retorna a TCB escolhida (ou None)
TipoFuncaoEscalonador = Callable[[list[TCB], TCB | None], TCB | None]

class Simulador:
    """
    Simula o Sistema Operacional: gerencia o relógio, filas de tarefas
    e coordena o escalonador e a CPU
    """

    def __init__(self, tarefas: list[TCB], funcao_escalonador: TipoFuncaoEscalonador, quantum: int):
        
        # Cria a CPU simulada com o quantum fornecido
        self.cpu = CPU(quantum_max=quantum)
        
        # Guarda a função de escalonamento (que veio externamente)
        self.funcao_escalonador = funcao_escalonador 

        # Gerencia de tarefas e relógio
        self.relogio_global = 0
        self.lista_de_tarefas_novas = sorted(tarefas, key=lambda t: t.tempo_ingresso)
        self.fila_de_prontos: list[TCB] = [] # fila de tarefas que podem ser escolhidas pelo escalonador
        self.lista_de_tarefas_terminadas: list[TCB] = []
        
        # Histórico para o gráfico de Gantt
        # Armazena: id da tarefa em execução e lista de ids das tarefas em pronto
        self.historico_execucao: list[tuple[int | None, list[int]]] = []

    def is_terminado(self) -> bool:
        """Verifica se a simulação terminou"""
        return (
            not self.lista_de_tarefas_novas and    # Sem tarefas novas
            not self.fila_de_prontos and           # Sem tarefas prontas
            self.cpu.tarefa_atual is None          # Sem tarefa em execução
        )

    def executar_passo(self) -> bool:
            """
            Executa um tick da simulação
            True se o passo foi executado, False se a simulação terminou
            """
            if self.is_terminado():
                return False  # Simulação concluída

            # Verifica chegadas de novas tarefas nesse tick
            for task in self.lista_de_tarefas_novas[:]:
                if task.tempo_ingresso == self.relogio_global:
                    task.estado = "Pronta"
                    self.fila_de_prontos.append(task)
                    self.lista_de_tarefas_novas.remove(task)

            # Lista de candidatos (lista de prontos + tarefa atual)
            candidatos = self.fila_de_prontos.copy()
            if self.cpu.tarefa_atual:
                candidatos.append(self.cpu.tarefa_atual) 

            if not candidatos:
                tarefa_escolhida = None
            else:
                # Pergunta ao escalonador qual tarefa deve rodar agora
                tarefa_escolhida = self.funcao_escalonador(candidatos, self.cpu.tarefa_atual)

            # Se a escolha do escalonador difere do que está na CPU, faz preempção e troca de contexto
            if self.cpu.tarefa_atual != tarefa_escolhida:
                if self.cpu.tarefa_atual:
                    tarefa_preemptida = self.cpu.remover_tarefa()
                    tarefa_preemptida.estado = "Pronta"
                    if tarefa_preemptida not in self.fila_de_prontos:
                        self.fila_de_prontos.append(tarefa_preemptida)
                
                # Coloca a tarefa escolhida na CPU (pode ser None)
                self.cpu.carregar_tarefa(tarefa_escolhida)
                if tarefa_escolhida and tarefa_escolhida in self.fila_de_prontos:
                    self.fila_de_prontos.remove(tarefa_escolhida)

            # A CPU executa um passo e retorna o resultado
            (tarefa_que_executou, evento) = self.cpu.executar_passo()
            
            # Processa o evento retornado pela CPU
            if evento == EventoCPU.TAREFA_CONCLUIDA:
                # a tarefa terminou
                self.lista_de_tarefas_terminadas.append(tarefa_que_executou)
            
            elif evento == EventoCPU.QUANTUM_EXPIRADO:
                # se o quantum acabou, coloca a tarefa de volta na fila de prontos
                self.fila_de_prontos.append(tarefa_que_executou)
            
            # Registra o estado deste tick para o gráfico de Gantt
            id_executado = tarefa_que_executou.id if tarefa_que_executou else None
            ids_prontos = [t.id for t in self.fila_de_prontos]
            
            # Correção para Gantt: Se quantum expirou, a tarefa executou neste tick.
            # Removemos ela da lista ids_prontos (para este registro)
            # para evitar que o Gantt mostre um bloco branco (Pronta) em vez de colorido
            if evento == EventoCPU.QUANTUM_EXPIRADO:
                if tarefa_que_executou.id in ids_prontos:
                    ids_prontos.remove(tarefa_que_executou.id)
            
            # Armazena no histórico a tupla (id_executado, lista_de_prontos)
            self.historico_execucao.append((id_executado, ids_prontos))

            # Avança o relógio global
            self.relogio_global += 1
            return True  # Passo executado