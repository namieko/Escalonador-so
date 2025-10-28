# interfaceGrafica.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tcb import TCB
import escalonador  # Importa o módulo de escalonamento
from simulador import Simulador # Importa o motor da simulação
import carregador  # Importa o módulo carregador
from copy import deepcopy # Necessário para reiniciar a simulação
from PIL import Image, ImageDraw, ImageFont # Para salvar a imagem do Gantt
from editor_tarefa_ui import EditorTarefaFrame # Importa o frame do editor
from gantt_canvas import GanttCanvas # <<<--- Importa a nova classe do canvas

class App:
    """
    Classe principal da GUI. Gerencia a janela, coordena o carregador,
    o simulador, o editor de tarefas e o canvas do Gantt.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonador de SO")
        self.root.geometry("1000x700")

        # --- Variáveis de Estado ---
        self.simulador: Simulador | None = None
        # Esta lista é a "fonte da verdade" para a configuração
        self.lista_de_tcbs: list[TCB] = []
        # <<<--- Variáveis de mapa de cores/linhas removidas --- >>>
        # (Agora são gerenciadas pelo GanttCanvas)

        # --- Parâmetros de Desenho Removidos ---
        # (Agora são gerenciados pelo GanttCanvas)

        # --- Frame Superior para Controles ---
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(fill=tk.X)

        # --- Botões de Ação ---
        self.btn_load = ttk.Button(control_frame, text="Carregar Arquivo", command=self.carregar_arquivo)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        self.btn_step = ttk.Button(control_frame, text="Próximo Passo",
                                   state=tk.DISABLED, command=self.executar_passo_gui)
        self.btn_step.pack(side=tk.LEFT, padx=5)
        self.btn_run_all = ttk.Button(control_frame, text="Execução Completa",
                                      state=tk.DISABLED, command=self.executar_tudo_gui)
        self.btn_run_all.pack(side=tk.LEFT, padx=5)

        # --- Seleção de Algoritmo ---
        ttk.Label(control_frame, text="Algoritmo:").pack(side=tk.LEFT, padx=(15, 2))
        self.algoritmos_disponiveis = list(escalonador.ALGORITMOS_REGISTRADOS.keys())
        self.combo_algoritmo = ttk.Combobox(
            control_frame, values=self.algoritmos_disponiveis, width=10, state="readonly"
        )
        self.combo_algoritmo.pack(side=tk.LEFT, padx=2)
        if self.algoritmos_disponiveis: self.combo_algoritmo.current(0)

        # --- Entrada do Quantum ---
        ttk.Label(control_frame, text="Quantum:").pack(side=tk.LEFT, padx=(15, 2))
        self.spin_quantum = tk.Spinbox(control_frame, from_=1, to=100, width=5)
        self.spin_quantum.pack(side=tk.LEFT, padx=2)

        # --- Relógio ---
        self.label_relogio = ttk.Label(control_frame, text="Relógio: 0", font=("Arial", 12, "bold"))
        self.label_relogio.pack(side=tk.RIGHT, padx=20)

        # --- Widget de Abas (Notebook) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # --- Aba 1: Gráfico de Gantt ---
        self.frame_gantt = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_gantt, text='Gráfico de Gantt')
        # <<<--- MUDANÇA: Cria uma instância da nossa classe GanttCanvas --- >>>
        self.gantt_chart = GanttCanvas(self.frame_gantt)
        self.gantt_chart.pack(expand=True, fill=tk.BOTH)
        # <<<------------------------------------------------------------- >>>

        # --- Aba 2: Detalhes dos Processos (Editor) ---
        self.frame_processos = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_processos, text='Detalhes dos Processos (Editor)')

        # Frame para a tabela
        tree_frame = ttk.Frame(self.frame_processos)
        tree_frame.pack(expand=True, fill=tk.BOTH)

        # Tabela (Treeview)
        cols = ('ID', 'Estado', 'Ingresso', 'Duração', 'Prioridade', 'Cor', 'Executado', 'Restante')
        self.tree_processos = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols:
            self.tree_processos.heading(col, text=col)
            width = 80
            if col in ('Estado', 'Cor'): width = 60
            if col in ('Executado', 'Restante'): width = 70
            self.tree_processos.column(col, width=width, anchor=tk.CENTER)
        self.tree_processos.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_processos.yview)
        self.tree_processos.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_processos.bind('<<TreeviewSelect>>', self.ao_selecionar_tarefa_para_edicao)

        # --- Frame para o Editor de Tarefa (Instância da classe separada) ---
        self.editor_frame = EditorTarefaFrame(self.frame_processos, self)
        self.editor_frame.pack(fill=tk.X, pady=10)

    # --- MÉTODOS DE CONTROLE E GUI ---

    def carregar_arquivo(self):
        """ Carrega configuração de um arquivo .txt """
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo de configuração", filetypes=[("Arquivos de Texto", "*.txt")]
        )
        if not caminho_arquivo: return
        try:
            dados = carregador.carregar_dados_configuracao(caminho_arquivo)
            self.lista_de_tcbs = dados.tarefas
            algoritmo_arquivo = dados.algoritmo_nome.upper()
            if algoritmo_arquivo in self.algoritmos_disponiveis:
                self.combo_algoritmo.set(algoritmo_arquivo)
            self.spin_quantum.delete(0, 'end'); self.spin_quantum.insert(0, str(dados.quantum))
            self.preparar_visualizacao_completa()
            messagebox.showinfo("Sucesso", f"{len(self.lista_de_tcbs)} processos carregados!")
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler ou processar o arquivo: {e}")
            self.lista_de_tcbs.clear()
            self.preparar_visualizacao_completa()

    def preparar_visualizacao_completa(self):
        """ Redesenha TODA a visualização (Gantt e Tabela) com base em self.lista_de_tcbs """
        self.resetar_simulacao() # Limpa o motor e reseta controles
        # <<<--- MUDANÇA: Limpa o canvas e a tabela --- >>>
        self.gantt_chart.limpar_tudo()
        self.tree_processos.delete(*self.tree_processos.get_children())

        if not self.lista_de_tcbs: return

        self.lista_de_tcbs.sort(key=lambda t: t.id)

        # <<<--- MUDANÇA: Delega o desenho do esqueleto do Gantt --- >>>
        self.gantt_chart.desenhar_esqueleto(self.lista_de_tcbs)

        # Preenche apenas a Tabela (Treeview) aqui
        for tcb in self.lista_de_tcbs:
            self.tree_processos.insert('', 'end', iid=tcb.id, values=(
                tcb.id, tcb.estado, tcb.tempo_ingresso, tcb.duracao_total,
                tcb.prioridade, tcb.cor, 0, tcb.duracao_total
            ))

        # Habilita botões
        self.btn_step.config(state=tk.NORMAL)
        self.btn_run_all.config(state=tk.NORMAL)
        if hasattr(self, 'editor_frame'):
            self.editor_frame.btn_adicionar_nova.config(state=tk.NORMAL)

    def resetar_simulacao(self):
        """ Reseta o simulador e os controles da GUI """
        self.simulador = None
        self.label_relogio.config(text="Relógio: 0")
        # Re-habilita controles globais
        self.btn_load.config(state=tk.NORMAL)
        self.combo_algoritmo.config(state="readonly")
        self.spin_quantum.config(state=tk.NORMAL)
        # Desabilita botões de simulação
        self.btn_step.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        # Chama o método desabilitar do editor
        if hasattr(self, 'editor_frame'):
            self.editor_frame.desabilitar()
            # Re-habilita o botão Adicionar Nova
            self.editor_frame.btn_adicionar_nova.config(state=tk.NORMAL)

    def ao_selecionar_tarefa_para_edicao(self, event):
        """ Chamado ao clicar na tabela. Pede ao EditorTarefaFrame para se preencher. """
        try:
            selected_item = self.tree_processos.focus()
            if not selected_item: return
            task_id = int(selected_item)
            tcb_para_editar = next((t for t in self.lista_de_tcbs if t.id == task_id), None)
            if tcb_para_editar and hasattr(self, 'editor_frame'):
                # Delega o preenchimento para o editor
                self.editor_frame.preparar_para_edicao(tcb_para_editar)
        except Exception as e:
            print(f"Erro ao selecionar tarefa: {e}")
            if hasattr(self, 'editor_frame'): self.editor_frame.desabilitar()

    def deselecionar_tabela(self):
        """ Remove a seleção da tabela Treeview. """
        if hasattr(self, 'tree_processos'):
            self.tree_processos.selection_remove(self.tree_processos.selection())

    def iniciar_simulacao_se_necessario(self) -> bool:
        """ Cria o objeto Simulador usando os dados atuais da lista_de_tcbs """
        if self.simulador: return True
        if not self.lista_de_tcbs:
            messagebox.showerror("Erro", "Nenhuma tarefa para simular.")
            return False
        try:
            algoritmo_str = self.combo_algoritmo.get()
            quantum = int(self.spin_quantum.get())
            funcao_escalonador = escalonador.get_escalonador_nome(algoritmo_str)
            tcbs_para_simulacao = deepcopy(self.lista_de_tcbs)
            self.simulador = Simulador(tcbs_para_simulacao, funcao_escalonador, quantum)
            self.desabilitar_controles_config() # Trava a configuração
            return True
        except Exception as e:
            messagebox.showerror("Erro ao Iniciar", f"Não foi possível iniciar o simulador: {e}")
            return False

    def desabilitar_controles_config(self):
        """ Trava os controles de configuração e o editor após o início da simulação """
        self.btn_load.config(state=tk.DISABLED)
        self.combo_algoritmo.config(state=tk.DISABLED)
        self.spin_quantum.config(state=tk.DISABLED)
        # Chama o desabilitar do editor
        if hasattr(self, 'editor_frame'):
             self.editor_frame.desabilitar()
             # Garante que o botão "Adicionar Nova" também seja desabilitado
             self.editor_frame.btn_adicionar_nova.config(state=tk.DISABLED)

    def executar_passo_gui(self):
        """ Executa um passo da simulação """
        if not self.iniciar_simulacao_se_necessario(): return
        if self.simulador.executar_passo():
            self.atualizar_gui_durante_simulacao()
        else:
            self.finalizar_simulacao()

    def executar_tudo_gui(self):
        """ Executa a simulação inteira """
        if not self.iniciar_simulacao_se_necessario(): return
        while self.simulador.executar_passo(): pass
        self.atualizar_gui_durante_simulacao()
        self.finalizar_simulacao()

    def atualizar_gui_durante_simulacao(self):
        """ Redesenha o estado atual (Relógio, Tabela, Gantt) """
        if not self.simulador: return

        # 1. Atualiza Relógio
        self.label_relogio.config(text=f"Relógio: {self.simulador.relogio_global}")

        # 2. Atualiza Tabela (Modo Debugger)
        todas_tarefas_sim = (
            self.simulador.lista_de_tarefas_novas + self.simulador.fila_de_prontos +
            self.simulador.lista_de_tarefas_terminadas
        )
        if self.simulador.cpu.tarefa_atual: todas_tarefas_sim.append(self.simulador.cpu.tarefa_atual)

        for tcb in todas_tarefas_sim:
            self.tree_processos.item(tcb.id, values=(
                tcb.id, tcb.estado, tcb.tempo_ingresso, tcb.duracao_total,
                tcb.prioridade, tcb.cor,
                tcb.tempo_executado, tcb.tempo_restante()
            ))

        # --- 3. Redesenha Gráfico de Gantt ---
        # <<<--- MUDANÇA: Delega o desenho dos blocos para o GanttCanvas --- >>>
        self.gantt_chart.atualizar_blocos(self.simulador.historico_execucao)
        # <<<-------------------------------------------------------------- >>>

    def finalizar_simulacao(self):
        """ Chamado quando a simulação termina """
        self.btn_step.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        # Re-habilita controles para nova simulação
        self.btn_load.config(state=tk.NORMAL)
        self.combo_algoritmo.config(state="readonly")
        self.spin_quantum.config(state=tk.NORMAL)
        if hasattr(self, 'editor_frame'): self.editor_frame.btn_adicionar_nova.config(state=tk.NORMAL)

        messagebox.showinfo("Simulação Concluída", f"A simulação terminou no relógio {self.simulador.relogio_global}.")
        self.gerar_imagem_final()

    def gerar_imagem_final(self):
        """ Salva o gráfico de Gantt como imagem (Req 2.3) """
        if not self.simulador or not self.simulador.historico_execucao:
            messagebox.showwarning("Nada para Salvar", "Execute uma simulação.", parent=self.root)
            return
        try:
            caminho_arquivo = filedialog.asksaveasfilename(
                title="Salvar Gráfico de Gantt",
                filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")],
                defaultextension=".png"
            )
            if not caminho_arquivo: return

            # <<<--- MUDANÇA: Pega parâmetros e mapas do GanttCanvas --- >>>
            g = self.gantt_chart # Apelido para facilitar
            num_tasks = len(self.lista_de_tcbs) # Usa a lista principal
            num_ticks = len(self.simulador.historico_execucao)
            margem_dir = 20; margem_inf = 50
            img_width = g.margem_esquerda + (num_ticks * g.tick_width) + margem_dir
            img_height = g.y_inicial + (num_tasks * g.altura_linha) + margem_inf

            try:
                fonte_label = ImageFont.truetype("arial.ttf", 16); fonte_regua = ImageFont.truetype("arial.ttf", 10)
            except IOError:
                fonte_label = ImageFont.load_default(); fonte_regua = ImageFont.load_default()

            img = Image.new('RGB', (img_width, img_height), 'white'); draw = ImageDraw.Draw(img)
            y_base_regua = -1

            # Usa a lista principal e os mapas/parâmetros do GanttCanvas
            for i, tcb in enumerate(sorted(self.lista_de_tcbs, key=lambda t: t.id)):
                y_pos = g.y_inicial + i * g.altura_linha # Usa g.y_inicial, g.altura_linha
                cor = g.mapa_cores.get(tcb.id, "black") # Usa g.mapa_cores
                draw.rectangle((10, y_pos - 15, 60, y_pos + 15), fill=cor, outline="black")
                draw.text((35, y_pos), f'T{tcb.id}', fill="white", font=fonte_label, anchor="mm")
                draw.line((g.margem_esquerda, y_pos, img_width - margem_dir, y_pos), fill="#ccc", width=1) # Usa g.margem_esquerda
                if i == num_tasks - 1: y_base_regua = y_pos + 30

            # Usa g.mapa_linhas_y, g.mapa_cores e g.tick_width
            for tick, (id_executado, ids_prontos) in enumerate(self.simulador.historico_execucao):
                x1 = g.margem_esquerda + tick * g.tick_width; x2 = x1 + g.tick_width # Usa g.margem_esquerda, g.tick_width
                for id_pronto in ids_prontos:
                    if id_pronto in g.mapa_linhas_y: # Usa g.mapa_linhas_y
                        y_pos = g.mapa_linhas_y[id_pronto]
                        draw.rectangle((x1, y_pos - 10, x2, y_pos + 10), fill="white", outline="#ccc")
                if id_executado is not None and id_executado in g.mapa_linhas_y: # Usa g.mapa_linhas_y
                    y_pos = g.mapa_linhas_y[id_executado]; cor = g.mapa_cores.get(id_executado, "black") # Usa g.mapa_cores
                    draw.rectangle((x1, y_pos - 10, x2, y_pos + 10), fill=cor, outline="black")

            # Usa g.margem_esquerda e g.tick_width
            if y_base_regua == -1: y_base_regua = 50
            for i in range(num_ticks + 1):
                x = g.margem_esquerda + i * g.tick_width # Usa g.margem_esquerda, g.tick_width
                draw.line((x, y_base_regua, x, y_base_regua + 5), fill="#555", width=1)
                if i % 5 == 0: draw.text((x, y_base_regua + 7), str(i), fill="black", font=fonte_regua, anchor="mt")

            img.save(caminho_arquivo)
            messagebox.showinfo("Sucesso", f"Gráfico salvo em:\n{caminho_arquivo}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Erro ao Salvar Imagem", f"Não foi possível salvar: {e}", parent=self.root)