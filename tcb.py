from dataclasses import dataclass, field
from typing import List

@dataclass
class TCB:
    """
    Bloco de Controle de Tarefa (Task Control Block).
    Guarda as informações de cada processo/tarefa.
    """
    
    # Atributos de cada tarefa
    id: int
    cor: str
    tempo_ingresso: int
    duracao_total: int
    prioridade: int
    # Campo para futura 'lista_eventos' (Req. 3.3.2)
    lista_eventos: List[str] = field(default_factory=list) 

    # Campos dinâmicos que serão atualizados durante a simulação
    estado: str = "Nova"
    tempo_executado: int = 0

    def tempo_restante(self) -> int:
        """Calcula o tempo que ainda falta para a tarefa terminar."""
        return self.duracao_total - self.tempo_executado