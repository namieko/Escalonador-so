# main.py
import tkinter as tk
import sys
from interfaceGrafica import App # A única coisa que ele precisa conhecer

def main():
    """Função principal que inicializa e executa a aplicação."""
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()