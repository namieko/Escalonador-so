# simulador.py
from tcb import TCB
from typing import Callable
from cpu import CPU, EventoCPU  

# Define um 'tipo' para a função de escalonador, para clareza
TipoFuncaoEscalonador = Callable[[list[TCB], TCB | None], TCB | None]

class Simulador:
    """
    Simula o Sistema Operacional: gerencia o relógio, filas de tarefas
    e coordena o escalonador e a CPU.
    """

    def __init__(self, tarefas: list[TCB], funcao_escalonador: TipoFuncaoEscalonador, quantum: int):
        
        # --- Hardware ---
        # O Simulador agora "tem" uma CPU 
        self.cpu = CPU(quantum_max=quantum)
        
        # --- SO / Escalonador ---
        self.funcao_escalonador = funcao_escalonador 

        # --- Gerenciamento de Processos (SO) ---
        self.relogio_global = 0
        self.lista_de_tarefas_novas = sorted(tarefas, key=lambda t: t.tempo_ingresso)
        self.fila_de_prontos: list[TCB] = []
        self.lista_de_tarefas_terminadas: list[TCB] = []
        
        # Histórico para o gráfico de Gantt
        # Armazena tuplas: (ID_executado, lista_de_IDs_prontos)
        self.historico_execucao: list[tuple[int | None, list[int]]] = []

    def is_terminado(self) -> bool:
        """Verifica se a simulação terminou."""
        return (
            not self.lista_de_tarefas_novas and    # Não há tarefas para chegar
            not self.fila_de_prontos and        # A fila de prontos está vazia
            self.cpu.tarefa_atual is None     # A CPU está ociosa
        )

    def executar_passo(self) -> bool:
            """
            Executa um único 'tick' do relógio da simulação.
            Retorna True se o passo foi executado, False se a simulação terminou.
            """
            if self.is_terminado():
                return False  # Simulação concluída

            # --- 1. SO: Verifica chegadas de novas tarefas ---
            for task in self.lista_de_tarefas_novas[:]:
                if task.tempo_ingresso == self.relogio_global:
                    task.estado = "Pronta"
                    self.fila_de_prontos.append(task)
                    self.lista_de_tarefas_novas.remove(task)

            # --- 2. SO: Executa o escalonador ---
            candidatos = self.fila_de_prontos.copy()
            if self.cpu.tarefa_atual:
                candidatos.append(self.cpu.tarefa_atual)

            if not candidatos:
                tarefa_escolhida = None
            else:
                tarefa_escolhida = self.funcao_escalonador(candidatos, self.cpu.tarefa_atual)

            # --- 3. SO: Processa a Troca de Contexto (Dispatch/Preempt) ---
            if self.cpu.tarefa_atual != tarefa_escolhida:
                if self.cpu.tarefa_atual:
                    tarefa_preemptida = self.cpu.remover_tarefa()
                    tarefa_preemptida.estado = "Pronta"
                    if tarefa_preemptida not in self.fila_de_prontos:
                        self.fila_de_prontos.append(tarefa_preemptida)
                
                self.cpu.carregar_tarefa(tarefa_escolhida)
                if tarefa_escolhida and tarefa_escolhida in self.fila_de_prontos:
                    self.fila_de_prontos.remove(tarefa_escolhida)

            # --- 4. Hardware: Executa o tick ---
            (tarefa_que_executou, evento) = self.cpu.executar_passo()
            
            # --- 5. SO: Processa o resultado do tick ---
            if evento == EventoCPU.TAREFA_CONCLUIDA:
                self.lista_de_tarefas_terminadas.append(tarefa_que_executou)
            
            elif evento == EventoCPU.QUANTUM_EXPIRADO:
                self.fila_de_prontos.append(tarefa_que_executou)
            
            # --- 6. SO: Registra o estado no histórico ---
            # (Esta é a seção corrigida)
            
            id_executado = tarefa_que_executou.id if tarefa_que_executou else None
            
            # Pega a lista de prontos *após* o processamento do evento
            ids_prontos = [t.id for t in self.fila_de_prontos]
            
            # Correção: Se a tarefa sofreu preempção por quantum,
            # ela já foi para a fila de prontos, mas não estava "pronta"
            # *durante* este tick (ela estava executando).
            if evento == EventoCPU.QUANTUM_EXPIRADO:
                if tarefa_que_executou.id in ids_prontos:
                    ids_prontos.remove(tarefa_que_executou.id)
            
            # Registra a tupla (o par) de valores
            self.historico_execucao.append((id_executado, ids_prontos))

            # --- 7. SO: Avança o relógio global ---
            self.relogio_global += 1
            return True  # Passo executado