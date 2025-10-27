# tcb.py (ATUALIZADO)
from dataclasses import dataclass, field
from typing import List

@dataclass
class TCB:
    """Representa o Bloco de Controle de Tarefa (TCB)."""
    
    # --- Atributos de Configuração (lidos do arquivo) ---
    id: int
    cor: str
    tempo_ingresso: int
    duracao_total: int
    prioridade: int
    
    # Adiciona o campo para 'lista_eventos' (Req. 3.3.2)
    # 'field(default_factory=list)' garante que seja uma lista vazia
    lista_eventos: List[str] = field(default_factory=list) 

    # --- Atributos de Estado (controlados pelo simulador) ---
    estado: str = "Nova"
    tempo_executado: int = 0

    def tempo_restante(self) -> int:
        """Calcula o tempo de CPU restante para a tarefa."""
        return self.duracao_total - self.tempo_executado