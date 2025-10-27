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
        # [cite_start]O Simulador agora "tem" uma CPU [cite: 21]
        self.cpu = CPU(quantum_max=quantum)
        
        # --- SO / Escalonador ---
        self.funcao_escalonador = funcao_escalonador 

        # --- Gerenciamento de Processos (SO) ---
        self.relogio_global = 0
        self.lista_de_tarefas_novas = sorted(tarefas, key=lambda t: t.tempo_ingresso)
        self.fila_de_prontos: list[TCB] = []
        self.lista_de_tarefas_terminadas: list[TCB] = []
        
        # [cite_start]Histórico para o gráfico de Gantt [cite: 30]
        self.historico_execucao: list[int | None] = []

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
        # (Lógica idêntica à anterior)
        for task in self.lista_de_tarefas_novas[:]:
            if task.tempo_ingresso == self.relogio_global:
                task.estado = "Pronta"
                self.fila_de_prontos.append(task)
                self.lista_de_tarefas_novas.remove(task)

        # --- 2. SO: Executa o escalonador ---
        # Os candidatos são a fila de prontos + a tarefa na CPU
        candidatos = self.fila_de_prontos.copy()
        if self.cpu.tarefa_atual:
            candidatos.append(self.cpu.tarefa_atual)

        if not candidatos:
            tarefa_escolhida = None
        else:
            # Pergunta ao escalonador qual tarefa deve rodar
            tarefa_escolhida = self.funcao_escalonador(candidatos, self.cpu.tarefa_atual)

        # --- 3. SO: Processa a Troca de Contexto (Dispatch/Preempt) ---
        # Compara a decisão do escalonador com quem está na CPU
        if self.cpu.tarefa_atual != tarefa_escolhida:
            
            # Preempção: Tira a tarefa antiga da CPU (se houver)
            if self.cpu.tarefa_atual:
                tarefa_preemptida = self.cpu.remover_tarefa()
                tarefa_preemptida.estado = "Pronta"
                if tarefa_preemptida not in self.fila_de_prontos:
                    self.fila_de_prontos.append(tarefa_preemptida)
            
            # Dispatch: Coloca a nova tarefa na CPU
            self.cpu.carregar_tarefa(tarefa_escolhida)
            # Remove a tarefa da fila de prontos (se ela estava lá)
            if tarefa_escolhida and tarefa_escolhida in self.fila_de_prontos:
                self.fila_de_prontos.remove(tarefa_escolhida)

        # --- 4. Hardware: Executa o tick ---
        # Manda a CPU executar o passo e reportar o que aconteceu
        (tarefa_que_executou, evento) = self.cpu.executar_passo()
        
        # Registra no histórico (mesmo se for ocioso)
        id_executado = tarefa_que_executou.id if tarefa_que_executou else None
        self.historico_execucao.append(id_executado)

        # --- 5. SO: Processa o resultado do tick ---
        # O SO reage ao que o hardware reportou
        if evento == EventoCPU.TAREFA_CONCLUIDA:
            # `tarefa_que_executou` é a TCB que terminou
            self.lista_de_tarefas_terminadas.append(tarefa_que_executou)
        
        elif evento == EventoCPU.QUANTUM_EXPIRADO:
            # `tarefa_que_executou` é a TCB que sofreu preempção
            self.fila_de_prontos.append(tarefa_que_executou)
        
        # (Se o evento for NADA, o SO não faz nada)

        # --- 6. SO: Avança o relógio global ---
        self.relogio_global += 1
        return True  # Passo executado