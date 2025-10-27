# cpu.py
from tcb import TCB
from enum import Enum, auto

class EventoCPU(Enum):
    """Eventos que a CPU reporta ao Simulador após um tick."""
    NADA = auto()             # Tarefa executou, nada de especial
    TAREFA_CONCLUIDA = auto()  # Tarefa terminou (tempo_restante == 0)
    QUANTUM_EXPIRADO = auto()  # Quantum da tarefa expirou

class CPU:
    """
    Representa um único processador (core) do sistema.
    Gerencia a execução da tarefa atual e o contador de quantum.
    """
    def __init__(self, quantum_max: int):
        self.tarefa_atual: TCB | None = None
        self.quantum_max = quantum_max
        self.tempo_no_quantum = 0

    def carregar_tarefa(self, tarefa: TCB | None):
        """
        Coloca uma nova tarefa na CPU (dispatch).
        Isso é chamado pelo Simulador.
        """
        self.tarefa_atual = tarefa
        self.tempo_no_quantum = 0 # Reseta o contador de quantum
        
        if self.tarefa_atual:
            self.tarefa_atual.estado = "Executando"

    def remover_tarefa(self) -> TCB | None:
        """
        Remove a tarefa atual da CPU (preempção).
        Retorna a tarefa que foi removida.
        """
        tarefa_preemptida = self.tarefa_atual
        self.tarefa_atual = None
        self.tempo_no_quantum = 0
        return tarefa_preemptida

    def executar_passo(self) -> tuple[TCB | None, EventoCPU]:
        """
        Executa um 'tick' na tarefa atual.
        Isso simula o "Passo 4" da sua lógica anterior.
        
        Retorna a tarefa que acabou de executar e um Evento
        para o Simulador (SO) saber o que fazer.
        """
        # Se a CPU estiver ociosa, não faz nada
        if self.tarefa_atual is None:
            return (None, EventoCPU.NADA)

        # --- Executa o tick ---
        self.tarefa_atual.tempo_executado += 1
        self.tempo_no_quantum += 1

        tarefa_que_executou = self.tarefa_atual

        # --- Verifica o estado PÓS-execução ---

        # 4a. A tarefa terminou?
        if self.tarefa_atual.tempo_restante() == 0:
            self.remover_tarefa() # Limpa a CPU
            tarefa_que_executou.estado = "Terminada"
            # Reporta ao "SO" que a tarefa terminou
            return (tarefa_que_executou, EventoCPU.TAREFA_CONCLUIDA)
        
        # 4b. O quantum estourou?
        if self.tempo_no_quantum == self.quantum_max:
            self.remover_tarefa() # Limpa a CPU
            tarefa_que_executou.estado = "Pronta"
            # Reporta ao "SO" que o quantum expirou
            return (tarefa_que_executou, EventoCPU.QUANTUM_EXPIRADO)

        # 4c. Nada especial, a tarefa continua
        return (tarefa_que_executou, EventoCPU.NADA)