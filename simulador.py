from tcb import TCB
from typing import Callable  # Importa o tipo 'Callable' (para funções)

# Define um 'tipo' para a função de escalonador, para clareza
TipoFuncaoEscalonador = Callable[[list[TCB], TCB | None], TCB | None]

class Simulador:
    """Simula a execução de um sistema operacional multitarefa preemptivo,
       gerenciando o estado e a lógica da simulação."""

    def __init__(self, tarefas: list[TCB], funcao_escalonador: TipoFuncaoEscalonador, quantum: int):
        # Configuração inicial
        self.quantum = int(quantum)
        
        # A função agora é recebida DIRETAMENTE!
        self.funcao_escalonador = funcao_escalonador 

        # Estado da simulação
        self.relogio_global = 0
        self.tempo_no_quantum = 0
        self.tarefa_na_cpu: TCB | None = None

        # Listas de Tarefas
        self.lista_de_tarefas_novas = sorted(tarefas, key=lambda t: t.tempo_ingresso)
        self.fila_de_prontos: list[TCB] = []
        self.lista_de_tarefas_terminadas: list[TCB] = []

        # Histórico para o gráfico de Gantt [cite: 30]
        # Armazena o ID da tarefa que executou em cada tick
        self.historico_execucao: list[int | None] = []

    def is_terminado(self) -> bool:
        """Verifica se a simulação terminou."""
        return (
            not self.lista_de_tarefas_novas and
            not self.fila_de_prontos and
            self.tarefa_na_cpu is None
        )

    def executar_passo(self) -> bool:
        """
        Executa um único 'tick' do relógio da simulação.
        Retorna True se o passo foi executado, False se a simulação terminou.
        """
        if self.is_terminado():
            return False  # Simulação concluída

        # --- 1. Verifica chegadas de novas tarefas ---
        # Move tarefas de "Novas" para "Prontas" se o tempo de ingresso for agora
        for task in self.lista_de_tarefas_novas[:]:  # Itera sobre uma cópia
            if task.tempo_ingresso == self.relogio_global:
                task.estado = "Pronta"
                self.fila_de_prontos.append(task)
                self.lista_de_tarefas_novas.remove(task)

        # --- 2. Decide quem *deveria* estar na CPU (Lógica de Preempção) ---
        # Os candidatos são: todas na fila de prontos + a que já está na CPU
        candidatos = self.fila_de_prontos.copy()
        if self.tarefa_na_cpu:
            # Adiciona a tarefa atual de volta à lista de candidatos
            # para que os escalonadores preemptivos (SRTF, Prioridade)
            # possam reavaliá-la contra as tarefas que acabaram de chegar.
            candidatos.append(self.tarefa_na_cpu)

        if not candidatos:
            # Ninguém para executar
            tarefa_escolhida = None
        else:
            # Aqui está a mágica:
            # Passamos TODOS os candidatos para suas funções de escalonamento.
            # Seu código SRTF e Prioridade encontrará o "melhor"
            # (menor tempo restante / maior prioridade) dessa lista.
            tarefa_escolhida = self.funcao_escalonador(candidatos, self.tarefa_na_cpu)

        # --- 3. Processa a Troca de Contexto (se necessária) ---
        if self.tarefa_na_cpu != tarefa_escolhida:
            # Houve preempção ou a CPU estava ociosa!
            
            # Se uma tarefa *estava* na CPU, ela foi preemptida
            if self.tarefa_na_cpu:
                self.tarefa_na_cpu.estado = "Pronta"
                if self.tarefa_na_cpu not in self.fila_de_prontos:
                    self.fila_de_prontos.append(self.tarefa_na_cpu)
            
            # Coloca a nova tarefa (ou None) na CPU
            self.tarefa_na_cpu = tarefa_escolhida
            
            if self.tarefa_na_cpu:
                self.tarefa_na_cpu.estado = "Executando"
                # Tira da fila de prontos (se estava lá)
                if self.tarefa_na_cpu in self.fila_de_prontos:
                    self.fila_de_prontos.remove(self.tarefa_na_cpu)
                
            # Reseta o contador do quantum
            self.tempo_no_quantum = 0

        # --- 4. Executa o tick na tarefa da CPU (se houver) ---
        if self.tarefa_na_cpu:
            # Incrementa o tempo de execução
            self.tarefa_na_cpu.tempo_executado += 1
            self.tempo_no_quantum += 1
            
            # Registra no histórico para o Gantt [cite: 30]
            self.historico_execucao.append(self.tarefa_na_cpu.id)
            
            # 4a. A tarefa terminou?
            if self.tarefa_na_cpu.tempo_restante() == 0:
                self.tarefa_na_cpu.estado = "Terminada"
                self.lista_de_tarefas_terminadas.append(self.tarefa_na_cpu)
                self.tarefa_na_cpu = None
                self.tempo_no_quantum = 0
            
            # 4b. O quantum estourou? (Preempção por tempo)
            elif self.tempo_no_quantum == self.quantum:
                self.tarefa_na_cpu.estado = "Pronta"
                self.fila_de_prontos.append(self.tarefa_na_cpu)
                self.tarefa_na_cpu = None
                self.tempo_no_quantum = 0
        else:
            # CPU Ociosa
            self.historico_execucao.append(None)
        
        # --- 5. Avança o relógio global ---
        self.relogio_global += 1
        return True  # Passo executado
