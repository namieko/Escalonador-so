from tcb import TCB
from enum import Enum, auto

# Define os tipos de eventos que a CPU pode gerar
# Enum pra evitar erros com strings
class EventoCPU(Enum):
    """Eventos que a CPU reporta ao Simulador após um tick."""
    NADA = auto()              # Tarefa executou, nada de especial
    TAREFA_CONCLUIDA = auto()  # Tarefa terminou (tempo_restante == 0)
    QUANTUM_EXPIRADO = auto()  # Quantum da tarefa expirou

class CPU:
    """
    Representa um único processador (core) do sistema.
    Gerencia a execução da tarefa atual e o quantum.
    """
    def __init__(self, quantum_max: int):
        self.tarefa_atual: TCB | None = None
        # Tempo máximo que uma tarefa pode executar sem ser preemptada
        self.quantum_max = quantum_max
        # Contador para saber quanto tempo a tarefa atual já executou nesse quantum
        self.tempo_no_quantum = 0

    def carregar_tarefa(self, tarefa: TCB | None):
        """
        Coloca uma nova tarefa na CPU.
        O simulador chama este método quando decide qual tarefa vai rodar.
        """
        self.tarefa_atual = tarefa
        self.tempo_no_quantum = 0 # Reseta o contador de quantum
        
        if self.tarefa_atual:
            self.tarefa_atual.estado = "Executando"

    def remover_tarefa(self) -> TCB | None:
        """
        Remove a tarefa atual da CPU.
        Retorna a tarefa que foi removida.
        """
        tarefa_preemptida = self.tarefa_atual
        self.tarefa_atual = None
        self.tempo_no_quantum = 0
        return tarefa_preemptida

    def executar_passo(self) -> tuple[TCB | None, EventoCPU]:
        """
        Simula a execução de um tick da CPU.
        Retorna a tarefa que executou e o evento ocorrido.
        """
        # Se não tem tarefa, não faz nada
        if self.tarefa_atual is None:
            return (None, EventoCPU.NADA)

        # Executa um tick na tarefa atual
        self.tarefa_atual.tempo_executado += 1
        self.tempo_no_quantum += 1

        tarefa_que_executou = self.tarefa_atual

        # Vê se a tarefa terminou
        if self.tarefa_atual.tempo_restante() == 0:
            self.remover_tarefa() # Limpa a CPU
            tarefa_que_executou.estado = "Terminada"
            # Reporta ao "SO" que a tarefa terminou
            return (tarefa_que_executou, EventoCPU.TAREFA_CONCLUIDA)
        
        # Vê se o quantum expirou
        if self.tempo_no_quantum == self.quantum_max:
            self.remover_tarefa() 
            tarefa_que_executou.estado = "Pronta"
            # Reporta ao "SO" que o quantum expirou
            return (tarefa_que_executou, EventoCPU.QUANTUM_EXPIRADO)

        # Senão, a tarefa continua executanto normalmente
        return (tarefa_que_executou, EventoCPU.NADA)