import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tcb import TCB
import escalonador  # Importa o módulo de escalonamento
from simulador import Simulador # Importa o motor da simulação
import carregador  # Importa o módulo carregador
from copy import deepcopy # Necessário para reiniciar a simulação
from PIL import Image, ImageDraw, ImageFont # Para salvar a imagem do Gantt
from editor_tarefa_ui import EditorTarefaFrame # Importa o frame do editor
from gantt_canvas import GanttCanvas # Canvas customizado para o gráfico de Gantt

class App:
    """
    Classe principal da GUI. Gerencia a janela, coordena o carregador,
    o simulador, o editor de tarefas e o canvas do Gantt.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonador de SO")
        self.root.geometry("1000x700")

        # Estado interno
        self.simulador: Simulador | None = None # Objeto que controla a execução
        self.lista_de_tcbs: list[TCB] = [] # Lista principal com os TCBs (carregados ou editados)

        # Frame Superior (barra de ferramentas)
        control_frame = ttk.Frame(root, padding="10")
        control_frame.pack(fill=tk.X)

        # Botões 
        self.btn_load = ttk.Button(control_frame, text="Carregar Arquivo", command=self.carregar_arquivo)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        self.btn_step = ttk.Button(control_frame, text="Próximo Passo",
                                   state=tk.DISABLED, command=self.executar_passo_gui)
        self.btn_step.pack(side=tk.LEFT, padx=5)
        self.btn_run_all = ttk.Button(control_frame, text="Execução Completa",
                                      state=tk.DISABLED, command=self.executar_tudo_gui)
        self.btn_run_all.pack(side=tk.LEFT, padx=5)

        # Seleção do algoritmo de escalonamento
        ttk.Label(control_frame, text="Algoritmo:").pack(side=tk.LEFT, padx=(15, 2))
        self.algoritmos_disponiveis = list(escalonador.ALGORITMOS_REGISTRADOS.keys())
        self.combo_algoritmo = ttk.Combobox(
            control_frame, values=self.algoritmos_disponiveis, width=10, state="readonly"
        )
        self.combo_algoritmo.pack(side=tk.LEFT, padx=2)
        if self.algoritmos_disponiveis: self.combo_algoritmo.current(0)

        # Entrada do Quantum
        ttk.Label(control_frame, text="Quantum:").pack(side=tk.LEFT, padx=(15, 2))
        self.spin_quantum = tk.Spinbox(control_frame, from_=1, to=100, width=5)
        self.spin_quantum.pack(side=tk.LEFT, padx=2)

        # Relógio global (exibe o tempo da simulação)
        self.label_relogio = ttk.Label(control_frame, text="Relógio: 0", font=("Arial", 12, "bold"))
        self.label_relogio.pack(side=tk.RIGHT, padx=20)

        # Widget de Abas 
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Aba 1: Gráfico de Gantt 
        self.frame_gantt = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_gantt, text='Gráfico de Gantt')
        #Cria uma instância de GanttCanvas 
        self.gantt_chart = GanttCanvas(self.frame_gantt)
        self.gantt_chart.pack(expand=True, fill=tk.BOTH)

        # Aba 2: Editor e tabela de processos
        self.frame_processos = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.frame_processos, text='Detalhes dos Processos (Editor)')

        # Tabela (Treeview) com tarefas
        tree_frame = ttk.Frame(self.frame_processos)
        tree_frame.pack(expand=True, fill=tk.BOTH)
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
        # Associa o evento de seleção na tabela ao método 'ao_selecionar_tarefa_para_edicao'
        self.tree_processos.bind('<<TreeviewSelect>>', self.ao_selecionar_tarefa_para_edicao)

        # Frame para o Editor de Tarefa (Instância da classe EditorTarefaFrame)
        self.editor_frame = EditorTarefaFrame(self.frame_processos, self)
        self.editor_frame.pack(fill=tk.X, pady=10)

    # MÉTODOS DE CONTROLE E GUI 

    def carregar_arquivo(self):
        """ Carrega configuração de um arquivo .txt """
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo de configuração", filetypes=[("Arquivos de Texto", "*.txt")]
        )
        if not caminho_arquivo: return
        # Tenta carregar e processar o arquivo
        try:
            # Chama a função do módulo 'carregador' para ler o arquivo
            dados = carregador.carregar_dados_configuracao(caminho_arquivo)
            # Atualiza a lista principal de TCBs desta classe com os dados lidos
            self.lista_de_tcbs = dados.tarefas
            # Atualiza os controles de algoritmo e quantum com os valores lidos
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
        self.resetar_simulacao() # Limpa o estado da simulação e reseta controles
        # A limpeza total do canvas do Gantt é a classe GanttCanvas que faz
        self.gantt_chart.limpar_tudo()
        # Limpa todas as linhas da tabela Treeview
        self.tree_processos.delete(*self.tree_processos.get_children())

        if not self.lista_de_tcbs: return

        self.lista_de_tcbs.sort(key=lambda t: t.id) # Ordena por ID 

        # Passa a lista de TCBs para o GanttCanvas desenhar o esqueleto
        self.gantt_chart.desenhar_esqueleto(self.lista_de_tcbs)

        # Preenche a Tabela (Treeview) 
        for tcb in self.lista_de_tcbs:
            self.tree_processos.insert('', 'end', iid=tcb.id, values=(
                tcb.id, tcb.estado, tcb.tempo_ingresso, tcb.duracao_total,
                tcb.prioridade, tcb.cor, 0, tcb.duracao_total
            ))

        # Habilita os botões de passo a passo e execução completa
        self.btn_step.config(state=tk.NORMAL)
        self.btn_run_all.config(state=tk.NORMAL)
        # Habilita o botão "Adicionar Nova" no editor (se o editor existir)
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
        # Desabilita botões de passo a passo e execução completa
        self.btn_step.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        # Chama o método desabilitar do editor
        if hasattr(self, 'editor_frame'):
            self.editor_frame.desabilitar()
            # Re-habilita o botão de adicionar nova tarefa
            self.editor_frame.btn_adicionar_nova.config(state=tk.NORMAL)

    def ao_selecionar_tarefa_para_edicao(self, event):
        """ Chamado ao clicar na tabela. Pede que o EditorTarefaFrame preencha """
        try:
            selected_item = self.tree_processos.focus() 
            if not selected_item: return
            # O ID da linha na Treeview é o ID da tarefa
            task_id = int(selected_item)
            # Encontra o objeto TCB correspondente na lista principal
            tcb_para_editar = next((t for t in self.lista_de_tcbs if t.id == task_id), None)
            if tcb_para_editar and hasattr(self, 'editor_frame'):
                # Delega o preenchimento para o editor
                self.editor_frame.preparar_para_edicao(tcb_para_editar)
        except Exception as e:
            print(f"Erro ao selecionar tarefa: {e}")
            if hasattr(self, 'editor_frame'): self.editor_frame.desabilitar()

    def deselecionar_tabela(self):
        """ Remove a seleção visual da tabela Treeview. """
        if hasattr(self, 'tree_processos'):
            self.tree_processos.selection_remove(self.tree_processos.selection())

    def iniciar_simulacao_se_necessario(self) -> bool:
        """ Cria o objeto Simulador usando os dados atuais da lista_de_tcbs """
        # Se o simulador já existe, não faz nada e retorna True
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
        # Chama o método 'executar_passo' do Simulador
        if self.simulador.executar_passo():
            self.atualizar_gui_durante_simulacao()
        else:
            self.finalizar_simulacao()

    def executar_tudo_gui(self):
        """ Executa a simulação inteira """
        if not self.iniciar_simulacao_se_necessario(): return
        # Loop enquanto 'executar_passo' do simulador retornar True
        while self.simulador.executar_passo(): pass
        self.atualizar_gui_durante_simulacao()
        self.finalizar_simulacao()

    def atualizar_gui_durante_simulacao(self):
        """ Redesenha o estado atual (Relógio, Tabela, Gantt) """
        if not self.simulador: return

        # Atualiza o relógio
        self.label_relogio.config(text=f"Relógio: {self.simulador.relogio_global}")

        # Atualiza a tabela 
        todas_tarefas_sim = (
            self.simulador.lista_de_tarefas_novas + self.simulador.fila_de_prontos +
            self.simulador.lista_de_tarefas_terminadas
        )
        if self.simulador.cpu.tarefa_atual: todas_tarefas_sim.append(self.simulador.cpu.tarefa_atual)
        # Para cada TCB da simulação, atualiza a linha correspondente na tabela
        for tcb in todas_tarefas_sim:
            self.tree_processos.item(tcb.id, values=(
                tcb.id, tcb.estado, tcb.tempo_ingresso, tcb.duracao_total,
                tcb.prioridade, tcb.cor,
                tcb.tempo_executado, tcb.tempo_restante()
            ))

        # Redesenha o gráfico de Gantt, passando o histórico atualizado pro GanttCanvas
        self.gantt_chart.atualizar_blocos(self.simulador.historico_execucao)

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
        self.gerar_imagem_final() # Salva a imagem do Gantt ao final

    def gerar_imagem_final(self):
        """ Salva o gráfico de Gantt como imagem PNG """
        if not self.simulador or not self.simulador.historico_execucao:
            messagebox.showwarning("Nada para Salvar", "Execute uma simulação.", parent=self.root)
            return
        try:
            caminho_arquivo = filedialog.asksaveasfilename(
                title="Salvar Gráfico de Gantt",
                filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")],
                defaultextension=".png"
            )
            if not caminho_arquivo: return # se o usuário cancelar

            # Pega parâmetros e mapas do GanttCanvas
            g = self.gantt_chart 
            num_tasks = len(self.lista_de_tcbs) # Usa a lista principal pra altura
            num_ticks = len(self.simulador.historico_execucao) #Usa o num de ticks do histórico pra largura
            margem_dir = 20; margem_inf = 50
            img_width = g.margem_esquerda + (num_ticks * g.tick_width) + margem_dir
            img_height = g.y_inicial + (num_tasks * g.altura_linha) + margem_inf

            try:
                fonte_label = ImageFont.truetype("arial.ttf", 16); fonte_regua = ImageFont.truetype("arial.ttf", 10)
            except IOError:
                fonte_label = ImageFont.load_default(); fonte_regua = ImageFont.load_default()
            # Cria a imagem em branco e o objeto de desenho
            img = Image.new('RGB', (img_width, img_height), 'white'); draw = ImageDraw.Draw(img)
            y_base_regua = -1

            # Usa a lista principal e os mapas/parâmetros do GanttCanvas, iterando sobre as tarefas
            for i, tcb in enumerate(sorted(self.lista_de_tcbs, key=lambda t: t.id)):
                y_pos = g.y_inicial + i * g.altura_linha # Usa g.y_inicial, g.altura_linha
                cor = g.mapa_cores.get(tcb.id, "black") # Usa g.mapa_cores
                draw.rectangle((10, y_pos - 15, 60, y_pos + 15), fill=cor, outline="black")
                draw.text((35, y_pos), f'T{tcb.id}', fill="white", font=fonte_label, anchor="mm")
                draw.line((g.margem_esquerda, y_pos, img_width - margem_dir, y_pos), fill="#ccc", width=1) # Usa g.margem_esquerda
                if i == num_tasks - 1: y_base_regua = y_pos + 30

            # Lógica similar à do GanttCanvas.atualizar_blocos, iterando sobre o histórico
            for tick, (id_executado, ids_prontos) in enumerate(self.simulador.historico_execucao):
                x1 = g.margem_esquerda + tick * g.tick_width; x2 = x1 + g.tick_width # Usa g.margem_esquerda, g.tick_width
                for id_pronto in ids_prontos:
                    if id_pronto in g.mapa_linhas_y: # Usa g.mapa_linhas_y
                        y_pos = g.mapa_linhas_y[id_pronto]
                        draw.rectangle((x1, y_pos - 10, x2, y_pos + 10), fill="white", outline="#ccc")
                if id_executado is not None and id_executado in g.mapa_linhas_y: # Usa g.mapa_linhas_y
                    y_pos = g.mapa_linhas_y[id_executado]; cor = g.mapa_cores.get(id_executado, "black") # Usa g.mapa_cores
                    draw.rectangle((x1, y_pos - 10, x2, y_pos + 10), fill=cor, outline="black")

            # Desenha o eixo do tempo 
            if y_base_regua == -1: y_base_regua = 50
            for i in range(num_ticks + 1):
                x = g.margem_esquerda + i * g.tick_width # Usa g.margem_esquerda, g.tick_width
                draw.line((x, y_base_regua, x, y_base_regua + 5), fill="#555", width=1)
                if i % 5 == 0: draw.text((x, y_base_regua + 7), str(i), fill="black", font=fonte_regua, anchor="mt")

            img.save(caminho_arquivo)
            messagebox.showinfo("Sucesso", f"Gráfico salvo em:\n{caminho_arquivo}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Erro ao Salvar Imagem", f"Não foi possível salvar: {e}", parent=self.root)