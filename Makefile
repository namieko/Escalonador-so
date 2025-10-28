# ==========================================================
# Makefile universal - Python + venv + PyInstaller
# Funciona em Windows (Chocolatey Make) e Linux
# ==========================================================

APP_NAME = simulador
VENV = .venv

# Detecta sistema e define caminhos automaticamente
ifeq ($(OS),Windows_NT)
	PYTHON = py
	PYTHON_VENV = $(VENV)/Scripts/python.exe
	RM = del /Q /F
	RMDIR = rmdir /S /Q
	NULL = nul
	RUN = dist\\$(APP_NAME).exe
else
	PYTHON = python3
	PYTHON_VENV = $(VENV)/bin/python
	RM = rm -f
	RMDIR = rm -rf
	NULL = /dev/null
	RUN = ./dist/$(APP_NAME)
endif

# ==========================================================
# Criação do ambiente virtual (com verificação automática)
# ==========================================================
$(VENV):
	@echo ">>> [Make] Criando ambiente virtual..."
ifeq ($(OS),Windows_NT)
	$(PYTHON) -m venv $(VENV)
else
	@if ! $(PYTHON) -m venv $(VENV) 2>/dev/null; then \
		echo ">>> [Make] python3-venv não encontrado. Instalando..."; \
		if command -v apt-get >/dev/null 2>&1; then \
			sudo apt-get update && sudo apt-get install -y python3-venv python3-tk; \
		elif command -v dnf >/dev/null 2>&1; then \
			sudo dnf install -y python3-venv python3-tkinter; \
		elif command -v pacman >/dev/null 2>&1; then \
			sudo pacman -Sy --noconfirm python-virtualenv tk; \
		else \
			echo ">>> [Make] Gerenciador de pacotes não reconhecido. Instale python3-venv e tkinter manualmente."; \
			exit 1; \
		fi; \
		echo ">>> [Make] Tentando novamente criar o ambiente virtual..."; \
		$(PYTHON) -m venv $(VENV); \
	fi
endif
	@echo ">>> [Make] Ambiente virtual criado com sucesso!"

# ==========================================================
# Instala as dependências
# ==========================================================
install: $(VENV)
	@echo ">>> [Make] Instalando dependências no ambiente virtual..."
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r requirements.txt
	@echo ">>> [Make] Dependências instaladas com sucesso!"

# ==========================================================
# Compila o executável standalone
# ==========================================================
build: install
	@echo ">>> [Make] Construindo executável standalone com PyInstaller..."
	$(PYTHON_VENV) -m PyInstaller --noconfirm --onefile --windowed main.py --name $(APP_NAME)
	@echo ""
	@echo "====== Build concluído! ======"
	@echo "O executável está em 'dist/$(APP_NAME)'."

# ==========================================================
# Executa o programa (após o build)
# ==========================================================
run: build
	@echo ">>> [Make] Executando $(APP_NAME)..."
	@$(RUN)

# ==========================================================
# Limpeza
# ==========================================================
clean:
	@echo ">>> [Make] Limpando arquivos temporários..."
	-$(RM) *.spec >$(NULL) 2>&1 || true
	-$(RMDIR) build >$(NULL) 2>&1 || true
	-$(RMDIR) dist >$(NULL) 2>&1 || true
	-$(RMDIR) __pycache__ >$(NULL) 2>&1 || true
	-$(RMDIR) $(VENV) >$(NULL) 2>&1 || true
	@echo ">>> [Make] Limpeza concluída!"
