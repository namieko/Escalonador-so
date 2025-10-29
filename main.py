import tkinter as tk
import sys

# Importa a classe 'App' do arquivo 'interfaceGrafica.py'
try:
    from interfaceGrafica import App
except ImportError:
    print("Erro: Não foi possível encontrar a classe 'App' no arquivo 'interfaceGrafica.py'.")
    sys.exit(1)

def main():
    """Função principal que inicializa e executa a aplicação."""
    
    try:
        # Cria a janela principal da aplicação
        root = tk.Tk()  
        
        # Cria a instância da GUI
        app = App(root)
        
        # Inicia o loop da interface
        root.mainloop()  
        
    except Exception as e:
        print(f"Ocorreu um erro fatal ao iniciar a aplicação: {e}")

# Ponto de Entrada 
if __name__ == "__main__":
    main()