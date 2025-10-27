# interfaceGrafica.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tcb import TCB
import escalonador  # Importa o módulo de escalonamento
from simulador import Simulador # Importa o motor da simulação
import carregador  # Importa o novo módulo carregador
from cpu import CPU # Importa a classe CPU (necessária para o type hint do Simulador)
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont
import os # Usaremos para extrair a extensão do arquivo

# O nome da classe é 'App', como no seu rascunho
class App:
    """
    Classe principal que gerencia a Interface Gráfica do Usuário (GUI)
    para o Simulador de Sistema Operacional.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonador de SO")
        self.root.geometry("1000x700") # Tamanho inicial da janela

        # --- Variáveis de Estado da Simulação ---
        self.simulador: Simulador | None = None # Armazena o *motor* da simulação
        self.lista_de_tcbs: list[TCB] = [] # Armazena os TCBs carregados
        self.mapa_cores = {} # Para mapear ID -> Cor
        self.mapa_linhas_gantt = {} # Para mapear ID -> Posição Y no Gantt
        
        # --- Parâmetros de Desenho do Gantt ---
        self.gantt_y_inicial = 50
        self.gantt_altura_linha = 40
        self.gantt_margem_esquerda = 70
        self.gantt_tick_width = 15 # Largura de 1 tick (em pixels)

        # --- Frame Superior para Controles ---
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(fill=tk.X)

        # --- Botões de Ação ---
        self.btn_load = ttk.Button(control_frame, text="Carregar Arquivo", command=self.carregar_arquivo)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        
        # Botões da simulação com seus comandos
        self.btn_step = ttk.Button(control_frame, text="Próximo Passo", 
                                   state=tk.DISABLED, command=self.executar_passo_gui)
        self.btn_step.pack(side=tk.LEFT, padx=5)
        
        self.btn_run_all = ttk.Button(control_frame, text="Execução Completa", 
                                      state=tk.DISABLED, command=self.executar_tudo_gui)
        self.btn_run_all.pack(side=tk.LEFT, padx=5)

        # --- Seleção de Algoritmo ---
        ttk.Label(control_frame, text="Algoritmo:").pack(side=tk.LEFT, padx=(15, 2))
        # Pega os algoritmos disponíveis DIRETAMENTE do módulo escalonador
        self.algoritmos_disponiveis = list(escalonador.ALGORITMOS_REGISTRADOS.keys())
        self.combo_algoritmo = ttk.Combobox(
            control_frame,
            values=self.algoritmos_disponiveis, 
            width=10,
            state="readonly"
        )
        self.combo_algoritmo.pack(side=tk.LEFT, padx=2)
        if self.algoritmos_disponiveis:
            self.combo_algoritmo.current(0) # Pré-seleciona o primeiro

        # --- Entrada do Quantum ---
        ttk.Label(control_frame, text="Quantum:").pack(side=tk.LEFT, padx=(15, 2))
        self.spin_quantum = tk.Spinbox(control_frame, from_=1, to=100, width=5)
        self.spin_quantum.pack(side=tk.LEFT, padx=2)
        
        # --- Relógio ---
        self.label_relogio = ttk.Label(control_frame, text="Relógio: 0", font=("Arial", 12, "bold"))
        self.label_relogio.pack(side=tk.RIGHT, padx=20)

        # --- Widget de Abas para Organizar a Visualização ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # --- Aba 1: Gráfico de Gantt ---
        self.frame_gantt = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_gantt, text='Gráfico de Gantt')
        
        # O Canvas para o gráfico é colocado DENTRO da aba de Gantt
        self.canvas_gantt = tk.Canvas(self.frame_gantt, bg="white")
        self.canvas_gantt.pack(expand=True, fill=tk.BOTH)
        
        # --- Aba 2: Gerenciador de Processos (Debugger) ---
        self.frame_processos = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_processos, text='Detalhes dos Processos (Debugger)')
        
        # (Melhoria) Usamos uma 'Treeview' (tabela) para o modo debugger
        cols = ('ID', 'Estado', 'Ingresso', 'Duração', 'Prioridade', 'Executado', 'Restante')
        self.tree_processos = ttk.Treeview(self.frame_processos, columns=cols, show='headings')
        for col in cols:
            self.tree_processos.heading(col, text=col)
            self.tree_processos.column(col, width=80, anchor=tk.CENTER)
        self.tree_processos.pack(expand=True, fill=tk.BOTH)


    # --- MÉTODOS DE CONTROLE ---

    def carregar_arquivo(self):
        """
        Pede ao usuário um arquivo e usa o módulo 'carregador'
        para processá-lo.
        """
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo de configuração",
            filetypes=[("Arquivos de Texto", "*.txt")]
        )
        if not caminho_arquivo:
            return # Usuário cancelou

        try:
            # Delega a lógica de leitura para o módulo 'carregador'
            dados = carregador.carregar_dados_configuracao(caminho_arquivo)
            
            # Atualiza a GUI com os dados recebidos
            self.lista_de_tcbs = dados.tarefas
            self.mapa_cores.clear()
            for tcb in dados.tarefas:
                self.mapa_cores[tcb.id] = tcb.cor
            
            # Atualiza os controles da interface
            algoritmo_arquivo = dados.algoritmo_nome.upper()
            if algoritmo_arquivo in self.algoritmos_disponiveis:
                self.combo_algoritmo.set(algoritmo_arquivo)
            
            self.spin_quantum.delete(0, 'end')
            self.spin_quantum.insert(0, str(dados.quantum))

            # Prepara a visualização (Gantt e Tabela)
            self.preparar_visualizacao()
            messagebox.showinfo("Sucesso", f"{len(self.lista_de_tcbs)} processos carregados com sucesso!")

        except Exception as e:
            # Captura qualquer erro que o 'carregador' lançou
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler ou processar o arquivo: {e}")
            self.lista_de_tcbs.clear()
            self.resetar_simulacao()

    def preparar_visualizacao(self):
        """ Prepara a Aba de Gantt e a Tabela de Processos com os dados carregados. """
        self.resetar_simulacao() # Reseta qualquer simulação anterior
        self.mapa_linhas_gantt.clear()
        self.canvas_gantt.delete("all")
        self.tree_processos.delete(*self.tree_processos.get_children())
        
        if not self.lista_de_tcbs:
            return

        # Desenha o nome de cada tarefa e uma linha base para ela
        for i, tcb in enumerate(self.lista_de_tcbs):
            y_pos = self.gantt_y_inicial + i * self.gantt_altura_linha
            self.mapa_linhas_gantt[tcb.id] = y_pos # Mapeia ID -> Posição Y
            
            # Caixa de cor e ID
            self.canvas_gantt.create_rectangle(10, y_pos - 15, 60, y_pos + 15, fill=tcb.cor, outline="black")
            self.canvas_gantt.create_text(35, y_pos, text=f'T{tcb.id}', fill="white", font=("Arial", 10, "bold"))
            
            # Linha de tempo
            self.canvas_gantt.create_line(self.gantt_margem_esquerda, y_pos, 2000, y_pos, fill="#ccc", dash=(2, 4))
            
            # Adiciona na tabela de processos (modo debugger)
            self.tree_processos.insert('', 'end', iid=tcb.id, values=(
                tcb.id, tcb.estado, tcb.tempo_ingresso, tcb.duracao_total,
                tcb.prioridade, tcb.tempo_executado, tcb.tempo_restante()
            ))
        
        # Desenha a régua de tempo (ticks)
        for i in range(100): # Desenha 100 ticks iniciais
            x = self.gantt_margem_esquerda + i * self.gantt_tick_width
            
            # Linhas dos ticks (movidas para cima, de -30 para -25)
            self.canvas_gantt.create_line(x, self.gantt_y_inicial - 30, x, self.gantt_y_inicial - 25, fill="#555")
            
            if i % 5 == 0: # Marca a cada 5 ticks
                # Texto (base do texto termina em -15, 5px acima do topo dos blocos)
                self.canvas_gantt.create_text(x, self.gantt_y_inicial - 15, text=str(i), anchor=tk.S, font=("Arial", 7))

        # Habilita os botões para iniciar a simulação
        self.btn_step.config(state=tk.NORMAL)
        self.btn_run_all.config(state=tk.NORMAL)

    def resetar_simulacao(self):
        """ Reseta a simulação, permitindo uma nova carga ou nova execução. """
        self.simulador = None
        self.label_relogio.config(text="Relógio: 0")
        
        # Habilita todos os controles de configuração
        self.btn_load.config(state=tk.NORMAL)
        self.combo_algoritmo.config(state="readonly")
        self.spin_quantum.config(state=tk.NORMAL)
        
        # Desabilita botões de simulação
        self.btn_step.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)

    def iniciar_simulacao_se_necessario(self) -> bool:
        """
        Cria o objeto Simulador na primeira vez que 'play' ou 'step' é clicado.
        Usa os valores ATUAIS dos widgets da GUI.
        """
        if self.simulador:  # Se o simulador já existe, não faz nada
            return True
        
        if not self.lista_de_tcbs:
            messagebox.showerror("Erro", "Nenhum processo carregado.")
            return False

        try:
            # Pega os valores da GUI
            algoritmo_str = self.combo_algoritmo.get()
            quantum = int(self.spin_quantum.get())
            
            # Pega a função de escalonamento
            funcao_escalonador = escalonador.get_escalonador_nome(algoritmo_str)
            
            # Cria o motor da simulação
            # É crucial criar cópias dos TCBs para permitir re-execução
            tcbs_para_simulacao = deepcopy(self.lista_de_tcbs)
            
            self.simulador = Simulador(tcbs_para_simulacao, funcao_escalonador, quantum)
            
            # Trava os controles de configuração (Req 3.1)
            self.desabilitar_controles_config()
            return True

        except Exception as e:
            messagebox.showerror("Erro ao Iniciar", f"Não foi possível iniciar o simulador: {e}")
            return False

    def desabilitar_controles_config(self):
        """ Trava os botões de configuração após o início da simulação. """
        self.btn_load.config(state=tk.DISABLED)
        self.combo_algoritmo.config(state=tk.DISABLED)
        self.spin_quantum.config(state=tk.DISABLED)

    def executar_passo_gui(self):
        """ Executa um único passo da simulação (Req 1.5.1) """
        if not self.iniciar_simulacao_se_necessario():
            return # Não conseguiu iniciar

        if self.simulador.executar_passo():
            self.atualizar_gui()
        else:
            self.finalizar_simulacao()

    def executar_tudo_gui(self):
        """ Executa a simulação inteira de uma vez (Req 1.5.2) """
        if not self.iniciar_simulacao_se_necessario():
            return
            
        # Executa o motor em loop
        while self.simulador.executar_passo():
            pass # Continua até o 'executar_passo' retornar False
        
        self.atualizar_gui() # Atualiza a GUI com o estado final
        self.finalizar_simulacao()

    def atualizar_gui(self):
        """ Redesenha o estado atual da simulação na tela (Req 1.5.1, 2.1) """
        if not self.simulador:
            return
            
        # 1. Atualiza o Relógio
        self.label_relogio.config(text=f"Relógio: {self.simulador.relogio_global}")
        
        # 2. Atualiza a Tabela de Processos (Modo Debugger)
        # Monta uma lista com todas as tarefas, de todas as filas
        todas_tarefas_sim = (
            self.simulador.lista_de_tarefas_novas +
            self.simulador.fila_de_prontos +
            self.simulador.lista_de_tarefas_terminadas
        )
        if self.simulador.cpu.tarefa_atual:
            todas_tarefas_sim.append(self.simulador.cpu.tarefa_atual)
            
        for tcb in todas_tarefas_sim:
            # Atualiza a linha da tabela correspondente a esta tarefa
            self.tree_processos.item(tcb.id, values=(
                tcb.id, tcb.estado, tcb.tempo_ingresso, tcb.duracao_total,
                tcb.prioridade, tcb.tempo_executado, tcb.tempo_restante()
            ))

        # --- 3. Redesenha o Gráfico de Gantt ---
        self.canvas_gantt.delete("execucao") # Limpa os blocos antigos

        # Percorre o histórico de execução (que agora tem (id_exec, lista_prontos))
        for tick, (id_executado, ids_prontos) in enumerate(self.simulador.historico_execucao):
            x1 = self.gantt_margem_esquerda + tick * self.gantt_tick_width
            x2 = x1 + self.gantt_tick_width

            # 1. Desenha os blocos de "Pronto" (Req 2.1 - ausência de cor)
            #    Isto é a barra "branca" do Maziero
            for id_pronto in ids_prontos:
                if id_pronto in self.mapa_linhas_gantt:
                    y_pos = self.mapa_linhas_gantt[id_pronto]
                    self.canvas_gantt.create_rectangle(
                        x1, y_pos - 10, x2, y_pos + 10, 
                        fill="white", outline="#ccc", tags="execucao"
                    )

            # 2. Desenha o bloco de "Executando" (Req 2.1 - cor)
            #    Este bloco desenha *por cima* do bloco "Pronto" se
            #    a tarefa estava pronta e foi escolhida no mesmo tick.
            if id_executado is not None:
                if id_executado in self.mapa_linhas_gantt:
                    cor = self.mapa_cores.get(id_executado, "black")
                    y_pos = self.mapa_linhas_gantt.get(id_executado)

                    self.canvas_gantt.create_rectangle(
                        x1, y_pos - 10, x2, y_pos + 10, 
                        fill=cor, outline="black", tags="execucao"
                    )

    def finalizar_simulacao(self):
        """ Chamado quando a simulação termina. """
        self.btn_step.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        
        # Re-habilita o botão de carregar para uma nova simulação
        self.btn_load.config(state=tk.NORMAL) 
        
        messagebox.showinfo("Simulação Concluída", 
                            f"A simulação terminou no relógio {self.simulador.relogio_global}.")
        
        # Aqui você chamaria a função para salvar a imagem (Req 2.3)
        self.gerar_imagem_final()


    def gerar_imagem_final(self):
        """
        Salva o gráfico de Gantt como um arquivo de imagem em alta resolução,
        desenhando-o manualmente com a Pillow. Cumpre o Requisito 2.3.
        """
        if not self.simulador or not self.simulador.historico_execucao:
            messagebox.showwarning("Nada para Salvar", "Execute uma simulação antes de salvar a imagem.", parent=self.root)
            return

        try:
            # 1. Pergunta ao usuário onde salvar
            caminho_arquivo = filedialog.asksaveasfilename(
                title="Salvar Gráfico de Gantt como Imagem",
                filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")],
                defaultextension=".png"
            )
            if not caminho_arquivo:
                print("Salvamento de imagem cancelado.")
                return

            # --- Parâmetros do Desenho ---
            num_tasks = len(self.lista_de_tcbs)
            num_ticks = len(self.simulador.historico_execucao)
            
            # Ajusta o tamanho da barra de ID (70px) e o tamanho de cada tick (15px)
            margem_dir = 20
            margem_inf = 50 # Espaço para a régua
            
            # Calcula o tamanho final da imagem
            img_width = self.gantt_margem_esquerda + (num_ticks * self.gantt_tick_width) + margem_dir
            img_height = self.gantt_y_inicial + (num_tasks * self.gantt_altura_linha) + margem_inf

            # Tenta carregar uma fonte (Arial). Se falhar, usa a fonte padrão.
            try:
                # Ajuste o tamanho da fonte se desejar
                fonte_label = ImageFont.truetype("arial.ttf", 16)
                fonte_regua = ImageFont.truetype("arial.ttf", 10)
            except IOError:
                print("Fonte 'arial.ttf' não encontrada. Usando fonte padrão.")
                fonte_label = ImageFont.load_default()
                fonte_regua = ImageFont.load_default()
            
            # --- Inicia o Desenho ---
            img = Image.new('RGB', (img_width, img_height), 'white')
            draw = ImageDraw.Draw(img)

            y_base_regua = -1 # Será calculado

            # 2. Desenha as Tarefas (Labels e Linhas-guia)
            for i, tcb in enumerate(sorted(self.lista_de_tcbs, key=lambda t: t.id)):
                y_pos = self.gantt_y_inicial + i * self.gantt_altura_linha
                cor = self.mapa_cores.get(tcb.id, "black")
                
                # Caixa de cor e ID
                draw.rectangle((10, y_pos - 15, 60, y_pos + 15), fill=cor, outline="black")
                draw.text((35, y_pos), f'T{tcb.id}', fill="white", font=fonte_label, anchor="mm")
                
                # Linha de tempo
                draw.line((self.gantt_margem_esquerda, y_pos, img_width - margem_dir, y_pos), fill="#ccc", width=1)
                
                # Guarda o Y da última tarefa para a régua
                if i == num_tasks - 1:
                    y_base_regua = y_pos + 30

            # 3. Desenha os Blocos de Execução (Pronto e Executando)
            for tick, (id_executado, ids_prontos) in enumerate(self.simulador.historico_execucao):
                x1 = self.gantt_margem_esquerda + tick * self.gantt_tick_width
                x2 = x1 + self.gantt_tick_width

                # Blocos "Pronto" (branco)
                for id_pronto in ids_prontos:
                    if id_pronto in self.mapa_linhas_gantt:
                        y_pos = self.mapa_linhas_gantt[id_pronto]
                        draw.rectangle((x1, y_pos - 10, x2, y_pos + 10), fill="white", outline="#ccc")
                
                # Bloco "Executando" (colorido)
                if id_executado is not None and id_executado in self.mapa_linhas_gantt:
                    y_pos = self.mapa_linhas_gantt[id_executado]
                    cor = self.mapa_cores.get(id_executado, "black")
                    draw.rectangle((x1, y_pos - 10, x2, y_pos + 10), fill=cor, outline="black")

            # 4. Desenha a Régua de Tempo
            if y_base_regua == -1: y_base_regua = 50 # Fallback
            
            for i in range(num_ticks + 1):
                x = self.gantt_margem_esquerda + i * self.gantt_tick_width
                draw.line((x, y_base_regua, x, y_base_regua + 5), fill="#555", width=1)
                if i % 5 == 0:
                    draw.text((x, y_base_regua + 7), str(i), fill="black", font=fonte_regua, anchor="mt")

            # 5. Salva a imagem
            img.save(caminho_arquivo)
            messagebox.showinfo("Sucesso", f"Gráfico salvo com sucesso em:\n{caminho_arquivo}", parent=self.root)

        except Exception as e:
            messagebox.showerror("Erro ao Salvar Imagem", f"Não foi possível salvar a imagem: {e}", parent=self.root)