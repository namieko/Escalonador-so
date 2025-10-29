import tkinter as tk
from tkinter import ttk, messagebox
from tcb import TCB

class EditorTarefaFrame(ttk.LabelFrame):
    """
    Frame que contém os widgets e a lógica para
    adicionar, editar e remover tarefas (TCBs)
    """
    # Construtor: recebe o frame pai (onde será colocado) e uma referência à classe App principal
    def __init__(self, parent_frame, app_ref):
        # Inicializa a classe pai (ttk.LabelFrame) com o título "Editor de Tarefa"
        super().__init__(parent_frame, text="Editor de Tarefa", padding=10)
        
        # Guarda uma referência à classe principal (App) para poder
        # acessar a lista_de_tcbs e chamar o método de redesenhar
        self.app = app_ref
        
        # Variável para guardar o ID da tarefa que está sendo editada
        # Se for None, significa que está no modo "Adicionar Nova"
        self.id_tarefa_em_edicao = None

        # Criação dos Widgets Internos do Editor 

        ttk.Label(self, text="ID da Tarefa:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.label_id_edicao = ttk.Label(self, text="N/A", font=("Arial", 10, "bold"))
        self.label_id_edicao.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(self, text="Tempo de Ingresso:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_ingresso = ttk.Entry(self, width=10)
        self.entry_ingresso.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Duração Total:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.entry_duracao = ttk.Entry(self, width=10)
        self.entry_duracao.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Prioridade:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.entry_prioridade = ttk.Entry(self, width=10)
        self.entry_prioridade.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(self, text="Cor (ex: red, #FF0000):").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.entry_cor = ttk.Entry(self, width=10)
        self.entry_cor.grid(row=2, column=3, padx=5, pady=5)

        # Frame separado para os botões do editor
        botoes_editor_frame = ttk.Frame(self)
        botoes_editor_frame.grid(row=0, column=4, rowspan=3, padx=20)

        # Botões com seus respectivos comandos (métodos desta classe)
        self.btn_adicionar_nova = ttk.Button(botoes_editor_frame, text="Adicionar Nova",
                                             command=self.nova_tarefa)
        self.btn_adicionar_nova.pack(fill=tk.X, pady=2)

        self.btn_salvar = ttk.Button(botoes_editor_frame, text="Salvar/Atualizar Tarefa",
                                     command=self.salvar_tarefa, state=tk.DISABLED)
        self.btn_salvar.pack(fill=tk.X, pady=2)

        self.btn_remover = ttk.Button(botoes_editor_frame, text="Remover Selecionada",
                                      command=self.remover_tarefa, state=tk.DISABLED)
        self.btn_remover.pack(fill=tk.X, pady=2)

        # Chama o método para deixar o editor limpo e desabilitado no início
        self.desabilitar()

    def desabilitar(self):
        """Limpa e desabilita todos os campos e botões do editor."""
        self.id_tarefa_em_edicao = None # Sai do modo de edição
        self.label_id_edicao.config(text="N/A") # Limpa o label do ID
        
        # Limpa e desabilita cada campo de entrada
        self.entry_ingresso.delete(0, 'end'); self.entry_ingresso.config(state=tk.DISABLED)
        self.entry_duracao.delete(0, 'end'); self.entry_duracao.config(state=tk.DISABLED)
        self.entry_prioridade.delete(0, 'end'); self.entry_prioridade.config(state=tk.DISABLED)
        self.entry_cor.delete(0, 'end'); self.entry_cor.config(state=tk.DISABLED)
        
        # Desabilita botões de ação
        self.btn_salvar.config(state=tk.DISABLED)
        self.btn_remover.config(state=tk.DISABLED)
        
        # Mantém o botão "Adicionar Nova" habilitado (a menos que a simulação esteja rodando)
        # O estado dele é controlado pela classe App

    def carregar_edicao(self, tcb):
        """Preenche o editor com os dados de um TCB existente (modo edição)"""
        self.id_tarefa_em_edicao = tcb.id
        self.label_id_edicao.config(text=str(tcb.id))

        # Habilita os campos
        self.entry_ingresso.config(state=tk.NORMAL)
        self.entry_duracao.config(state=tk.NORMAL)
        self.entry_prioridade.config(state=tk.NORMAL)
        self.entry_cor.config(state=tk.NORMAL)
        self.btn_salvar.config(state=tk.NORMAL)
        self.btn_remover.config(state=tk.NORMAL)

        # Limpa e insere os valores do TCB
        self.entry_ingresso.delete(0, 'end'); self.entry_ingresso.insert(0, str(tcb.tempo_ingresso))
        self.entry_duracao.delete(0, 'end'); self.entry_duracao.insert(0, str(tcb.duracao_total))
        self.entry_prioridade.delete(0, 'end'); self.entry_prioridade.insert(0, str(tcb.prioridade))
        self.entry_cor.delete(0, 'end'); self.entry_cor.insert(0, tcb.cor)

    def nova_tarefa(self):
        """Limpa o editor e preenche com valores padrão para adicionar uma nova tarefa."""
        self.id_tarefa_em_edicao = None # Entra no modo "Adicionar"
        
        # Deseleciona qualquer item na tabela principal (chamando método da App)
        self.app.deselecionar_tabela() 
        
        # Calcula o próximo ID disponível (maior ID na lista da App + 1)
        new_id = max([t.id for t in self.app.lista_de_tcbs] + [0]) + 1
        self.label_id_edicao.config(text=str(new_id))

        # Habilita os campos e o botão de salvar
        self.entry_ingresso.config(state=tk.NORMAL)
        self.entry_duracao.config(state=tk.NORMAL)
        self.entry_prioridade.config(state=tk.NORMAL)
        self.entry_cor.config(state=tk.NORMAL)
        self.btn_salvar.config(state=tk.NORMAL)
        self.btn_remover.config(state=tk.DISABLED) # Não pode remover o que não existe

        # Limpa e insere valores padrão sugeridos
        self.entry_ingresso.delete(0, 'end'); self.entry_ingresso.insert(0, "0")
        self.entry_duracao.delete(0, 'end'); self.entry_duracao.insert(0, "5")
        self.entry_prioridade.delete(0, 'end'); self.entry_prioridade.insert(0, "1")
        self.entry_cor.delete(0, 'end'); self.entry_cor.insert(0, "gray")

    def salvar_tarefa(self):
        """Salva uma nova tarefa ou atualiza uma existente na lista principal da App"""
        # try para capturar erros de digitação/validação
        try: 
            # Pega os valores dos campos
            novo_ingresso = int(self.entry_ingresso.get())
            nova_duracao = int(self.entry_duracao.get())
            nova_prioridade = int(self.entry_prioridade.get())
            nova_cor = self.entry_cor.get()
            
            # Validações básicas
            if not nova_cor: raise ValueError("A cor não pode estar vazia.")
            if nova_duracao <= 0: raise ValueError("Duração deve ser maior que zero.")

            # Verifica se está em modo EDIÇÃO (id_tarefa_em_edicao tem um número)
            if self.id_tarefa_em_edicao is not None:
                # Encontra o TCB na lista principal (da App) e o atualiza
                tcb_para_editar = next((t for t in self.app.lista_de_tcbs if t.id == self.id_tarefa_em_edicao), None)
                if tcb_para_editar:
                    tcb_para_editar.tempo_ingresso = novo_ingresso
                    tcb_para_editar.duracao_total = nova_duracao
                    tcb_para_editar.prioridade = nova_prioridade
                    tcb_para_editar.cor = nova_cor
                    messagebox.showinfo("Sucesso", f"Tarefa T{tcb_para_editar.id} atualizada.", parent=self.app.root)
            # Senão, está em modo CRIAÇÃO (id_tarefa_em_edicao é None)
            else:
                novo_id = int(self.label_id_edicao.cget("text"))
                # Verifica se ID já existe na lista principal (da App)
                if any(t.id == novo_id for t in self.app.lista_de_tcbs):
                    raise ValueError(f"O ID {novo_id} já está em uso.")
                
                # Cria o novo TCB
                novo_tcb = TCB(
                    id=novo_id, tempo_ingresso=novo_ingresso, duracao_total=nova_duracao,
                    prioridade=nova_prioridade, cor=nova_cor
                )
                # Adiciona na lista principal (da App)
                self.app.lista_de_tcbs.append(novo_tcb)
                messagebox.showinfo("Sucesso", f"Tarefa T{novo_tcb.id} criada.", parent=self.app.root)

            # Chama o método da App para redesenhar toda a interface (Gantt e Tabela)
            self.app.preparar_visualizacao()

        except ValueError as e:
            messagebox.showerror("Erro de Formato", f"Erro nos dados: {e}. Verifique os campos.", parent=self.app.root)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar a tarefa: {e}", parent=self.app.root)

    def remover_tarefa(self):
        """Remove a tarefa selecionada no editor da lista principal da App"""
        if self.id_tarefa_em_edicao is None: return

        # Encontra a tarefa na lista principal (da App)
        tcb_para_remover = next((t for t in self.app.lista_de_tcbs if t.id == self.id_tarefa_em_edicao), None)
        if not tcb_para_remover: return

        if messagebox.askyesno("Confirmar Remoção", f"Remover Tarefa T{tcb_para_remover.id}?", parent=self.app.root):
            # Remove da lista principal (da App)
            self.app.lista_de_tcbs.remove(tcb_para_remover)
            messagebox.showinfo("Removido", f"Tarefa T{tcb_para_remover.id} removida.", parent=self.app.root)
            # Chama o método da App para redesenhar toda a interface
            self.app.preparar_visualizacao()