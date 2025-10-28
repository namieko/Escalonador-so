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
else
	PYTHON = python3
	PYTHON_VENV = $(VENV)/bin/python
	RM = rm -f
	RMDIR = rm -rf
	NULL = /dev/null
endif

# ==========================================================
# Criação do ambiente virtual
# ==========================================================
$(VENV):
	@echo Criando ambiente virtual...
	$(PYTHON) -m venv $(VENV)

# ==========================================================
# Instala as dependências
# ==========================================================
install: $(VENV)
	@echo Instalando dependências no ambiente virtual...
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r requirements.txt
	@echo Dependências instaladas com sucesso!

# ==========================================================
# Compila o executável standalone
# ==========================================================
build: install
	@echo Construindo executável standalone com PyInstaller...
	$(PYTHON_VENV) -m PyInstaller --noconfirm --onefile --windowed main.py --name $(APP_NAME)
	@echo.
	@echo ====== Build concluído! ======
	@echo O executável está em "dist/$(APP_NAME)".

# ==========================================================
# Limpeza
# ==========================================================
clean:
	@echo Limpando arquivos temporários...
	-$(RM) *.spec >$(NULL) 2>&1 || true
	-$(RMDIR) build >$(NULL) 2>&1 || true
	-$(RMDIR) dist >$(NULL) 2>&1 || true
	-$(RMDIR) __pycache__ >$(NULL) 2>&1 || true
	-$(RMDIR) $(VENV) >$(NULL) 2>&1 || true
	@echo Limpeza concluída!
