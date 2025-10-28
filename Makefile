# ==========================================================
# Makefile universal - Simulador de Escalonamento de SO
# Funciona em Windows (via Chocolatey Make) e Linux
# ==========================================================

# Nome base do executável
APP_NAME = simulador

# Detecta automaticamente o sistema operacional
ifeq ($(OS),Windows_NT)
	PYTHON = py
	RM = del /Q /F
	RMDIR = rmdir /S /Q
else
	PYTHON = python3
	RM = rm -f
	RMDIR = rm -rf
endif

# ==========================================================
# Alvo: install
# Instala dependências necessárias (PyInstaller e Pillow)
# ==========================================================
install:
	@echo Instalando dependências...
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# ==========================================================
# Alvo: build
# Cria o executável standalone usando o PyInstaller
# ==========================================================
build:
	@echo Construindo executável standalone...
	$(PYTHON) -m PyInstaller --noconfirm --onefile --windowed main.py --name $(APP_NAME)
	@echo.
	@echo ====== Build concluído! ======
	@echo O executável está na pasta "dist/$(APP_NAME)".
	@echo.

# ==========================================================
# Alvo: clean
# Remove arquivos temporários e de build
# ==========================================================
clean:
	@echo Limpando arquivos temporários...
	-$(RM) *.spec 2>nul || true
	-$(RMDIR) build 2>nul || true
	-$(RMDIR) dist 2>nul || true
	-$(RMDIR) __pycache__ 2>nul || true
	@echo Limpeza concluída.
