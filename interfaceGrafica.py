import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tcb import TCB
import escalonador
from simulador import Simulador
import carregador  # <--- 1. IMPORTA O NOVO MÓDULO

class App:
    def __init__(self, root):
        self.root = root
        # ... (todo o resto do __init__ continua igual) ...
        # ... (criação de botões, abas, etc) ...

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
            # <--- 2. DELEGA A LÓGICA DE LEITURA ---
            # Toda a lógica de 'open', 'readline', 'split' foi movida
            dados = carregador.carregar_dados_configuracao(caminho_arquivo)
            
            # --- 3. ATUALIZA A GUI COM OS DADOS RECEBIDOS ---
            self.lista_de_tcbs = dados.tarefas
            self.mapa_cores.clear()
            for tcb in dados.tarefas:
                self.mapa_cores[tcb.id] = tcb.cor
            
            # Atualiza os controles da interface
            algoritmo_arquivo = dados.algoritmo_nome.upper()
            if algoritmo_arquivo in self.algoritmos_disponiveis:
                self.combo_algoritmo.set(algoritmo_arquivo)
            
            self.spin_quantum.delete(0, 'end')
            self.spin_quantum.insert(0, str(dados.quantum)) # Converte int para str

            self.preparar_visualizacao()
            messagebox.showinfo("Sucesso", f"{len(self.lista_de_tcbs)} processos carregados com sucesso!")

        except Exception as e:
            # Captura qualquer erro que o 'carregador' lançou
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler ou processar o arquivo: {e}")
            self.lista_de_tcbs.clear()
            self.resetar_simulacao()

    # ... (o resto dos métodos da GUI continuam iguais) ...
    # preparar_visualizacao, iniciar_simulacao, executar_passo_gui, etc.