# main.py
import tkinter as tk
import sys

# 1. Importa a classe 'App' do arquivo 'interfaceGrafica.py'
try:
    from interfaceGrafica import App
except ImportError:
    print("Erro: Não foi possível encontrar a classe 'App' no arquivo 'interfaceGrafica.py'.")
    sys.exit(1)

def main():
    """Função principal que inicializa e executa a aplicação."""
    
    try:
        root = tk.Tk()  # Cria a janela principal da aplicação
        
        # 2. Cria a instância da sua GUI
        app = App(root)
        
        # 3. Inicia o loop da interface
        root.mainloop()  # Espera por cliques do usuário
        
    except Exception as e:
        print(f"Ocorreu um erro fatal ao iniciar a aplicação: {e}")

# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    main()