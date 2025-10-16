from dataclasses import dataclass

@dataclass
class TCB:
    """Representa o Bloco de Controle de Tarefa (TCB)."""
    id: int
    cor: str
    tempo_ingresso: int
    duracao_total: int
    prioridade: int
    estado: str = "Nova"
    tempo_executado: int = 0

    def tempo_restante(self) -> int:
        return self.duracao_total - self.tempo_executado