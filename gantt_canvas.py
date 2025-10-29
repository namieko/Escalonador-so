import tkinter as tk
from tcb import TCB

class GanttCanvas(tk.Canvas):
    """
    Um widget Canvas especializado para desenhar o Gráfico de Gantt.
    """
    def __init__(self, parent_frame, **kwargs):
        # Chama o construtor do tk.Canvas original
        super().__init__(parent_frame, bg="white", **kwargs)

        # Parâmetros de desenho 
        self.y_inicial = 50
        self.altura_linha = 40
        self.margem_esquerda = 70
        self.tick_width = 15

        # Dicionários internos para guardar cores e posições
        self.mapa_cores = {}
        self.mapa_linhas_y = {}

    def limpar_tudo(self):
        """Apaga todo o conteúdo do canvas."""
        self.delete(tk.ALL)
        self.mapa_cores.clear()
        self.mapa_linhas_y.clear()

    def limpar_blocos_execucao(self):
        """Apaga apenas os blocos de execução (mantém o esqueleto)."""
        self.delete("execucao") # Usa a tag definida ao criar os blocos

    def desenhar_esqueleto(self, tcbs):
        """
        Desenha as linhas, labels das tarefas e a régua de tempo.
        Deve ser chamado uma vez após carregar as tarefas.
        """
        self.limpar_tudo()
        if not tcbs: return

        # Ordena por ID 
        tcbs_ordenados = sorted(tcbs, key=lambda t: t.id)

        # Desenha cada linha de tarefa, iterando sobre a lista de tarefas
        for i, tcb in enumerate(tcbs_ordenados):
            self.mapa_cores[tcb.id] = tcb.cor # Guarda a cor, usando o ID como chave
            y_pos = self.y_inicial + i * self.altura_linha
            self.mapa_linhas_y[tcb.id] = y_pos # Guarda a posição Y, usando o ID como chave

            # Caixa de cor e ID
            self.create_rectangle(10, y_pos - 15, 60, y_pos + 15, fill=tcb.cor, outline="black")
            self.create_text(35, y_pos, text=f'T{tcb.id}', fill="white", font=("Arial", 10, "bold"))
            # Linha guia
            self.create_line(self.margem_esquerda, y_pos, 2000, y_pos, fill="#ccc", dash=(2, 4))

        # Desenha a régua de tempo
        for i in range(100): # Desenha 100 ticks iniciais
            x = self.margem_esquerda + i * self.tick_width
            # Linhas dos ticks
            self.create_line(x, self.y_inicial - 30, x, self.y_inicial - 25, fill="#555")
            if i % 5 == 0: # Marca a cada 5 ticks
                # faz o texto ficar acima da linha da primeira tarefa
                self.create_text(x, self.y_inicial - 15, text=str(i), anchor=tk.S, font=("Arial", 7))

    def atualizar_blocos(self, historico):
        """
        Desenha os blocos de execução (Pronto e Executando) com base
        no histórico fornecido pelo simulador.
        """
        self.limpar_blocos_execucao() # Apaga os blocos antigos

        # Itera sobre o histórico
        # 'enumerate' fornece o índice (tick) e o valor (tupla)
        for tick, (id_executado, ids_prontos) in enumerate(historico):
            x1 = self.margem_esquerda + tick * self.tick_width
            x2 = x1 + self.tick_width

            # Blocos "Pronto" (branco)
            for id_pronto in ids_prontos:
                if id_pronto in self.mapa_linhas_y:
                    y_pos = self.mapa_linhas_y[id_pronto]
                    self.create_rectangle(
                        x1, y_pos - 10, x2, y_pos + 10,
                        fill="white", outline="#ccc", tags="execucao" # Usa a tag
                    )

            # Bloco "Executando" (colorido)
            if id_executado is not None and id_executado in self.mapa_linhas_y:
                cor = self.mapa_cores.get(id_executado, "black")
                y_pos = self.mapa_linhas_y.get(id_executado)
                self.create_rectangle(
                    x1, y_pos - 10, x2, y_pos + 10,
                    fill=cor, outline="black", tags="execucao" # Usa a tag
                )