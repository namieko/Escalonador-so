# ==========================================================
# Makefile - Projeto: Simulador de Escalonamento de SO
# ==========================================================
# Automatiza o processo de configuração, instalação e compilação
# do projeto Python usando ambiente virtual e PyInstaller.
#
# --- Pré-requisitos do Sistema ---
# Antes de usar este Makefile, certifique-se de que os seguintes
# softwares estejam instalados no seu sistema:
# 1. Python 3 (python3)
# 2. Pip (python3-pip)
# 3. Módulo venv do Python (python3-venv) - essencial para criar o ambiente virtual.
# 4. Módulo Tkinter do Python (python3-tk) - essencial para a interface gráfica.
# 5. Make (make) - a ferramenta para rodar este arquivo.
# 6. Git (git) - opcional, apenas para clonar o repositório.
#
# Comandos de Instalação:
#   Debian/Ubuntu: sudo apt install python3 python3-pip python3-venv python3-tk make git
#   Fedora/CentOS: sudo dnf install python3 python3-pip python3-virtualenv tkinter tk-devel make git
#   Arch Linux: sudo pacman -Syu python python-pip python-virtualenv tk make git
# ==========================================================

APP_NAME = simulador
VENV = .venv

# Detecta automaticamente o sistema operacional
ifeq ($(OS),Windows_NT)
	PYTHON = py
	PYTHON_VENV = $(VENV)/Scripts/python.exe
	RM = del /Q /F
	RMDIR = rmdir /S /Q
	NULL = nul
	RUN = dist\\$(APP_NAME).exe
	SHELLTYPE = cmd
else
	PYTHON = python3
	PYTHON_VENV = $(VENV)/bin/python
	RM = rm -f
	RMDIR = rm -rf
	NULL = /dev/null
	RUN = ./dist/$(APP_NAME)
	SHELLTYPE = bash
endif

# Criação do ambiente virtual (venv)
$(VENV):
	@echo ">>> [Make] Criando ambiente virtual..."
	@$(PYTHON) -m venv $(VENV) || { \
		echo "❌ Erro: não foi possível criar o ambiente virtual."; \
		echo "Verifique se o pacote 'python3-venv' está instalado."; \
		exit 1; \
	}
	@echo ">>> [Make] Ambiente virtual criado com sucesso!"

# Instala dependências no ambiente virtual
install: $(VENV)
	@echo ">>> [Make] Instalando dependências..."
	@$(PYTHON_VENV) -m pip install --upgrade pip
	@$(PYTHON_VENV) -m pip install -r requirements.txt
	@echo ">>> [Make] Dependências instaladas com sucesso!"

# Compila o executável standalone
build: install
	@echo ">>> [Make] Verificando dependências do sistema..."
ifeq ($(OS),Windows_NT)
	@$(PYTHON_VENV) -c "import tkinter" || ( \
		echo "⚠️  Tkinter não encontrado."; \
		echo "Instale com: py -m pip install tk (ou reinstale o Python com suporte a GUI)."; \
		exit /b 1 )
else
	@$(PYTHON_VENV) -c "import tkinter" 2>/dev/null || { \
		echo "⚠️  Tkinter não encontrado."; \
		echo "Instale com: sudo apt install python3-tk (Debian/Ubuntu)"; \
		echo "              sudo dnf install python3-tkinter (Fedora)"; \
		echo "              sudo pacman -Sy tk (Arch)"; \
		exit 1; \
	}
endif
	@echo ">>> [Make] Tkinter disponível. Prosseguindo com a compilação..."

	@echo ">>> [Make] Construindo executável standalone..."
	@$(PYTHON_VENV) -m PyInstaller --noconfirm --onefile --windowed main.py --name $(APP_NAME)
	@echo ""
	@echo "====== ✅ Build concluído ======"
	@echo "Executável disponível em: dist/$(APP_NAME)"
	@echo ""

# Executa o programa (após build)
run: build
	@echo ">>> [Make] Executando $(APP_NAME)..."
	@$(RUN)

# Limpeza de arquivos temporários
clean:
	@echo ">>> [Make] Limpando arquivos temporários..."
	-$(RM) *.spec >$(NULL) 2>&1 || true
	-$(RMDIR) build >$(NULL) 2>&1 || true
	-$(RMDIR) dist >$(NULL) 2>&1 || true
	-$(RMDIR) __pycache__ >$(NULL) 2>&1 || true
	-$(RMDIR) $(VENV) >$(NULL) 2>&1 || true
	@echo ">>> [Make] Limpeza concluída!"
