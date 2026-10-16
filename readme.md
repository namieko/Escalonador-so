# Simulador

Software desenvolvido em Python projetado para ser empacotado e executado como uma aplicação *standalone* (autossuficiente), compatível com ambientes **Linux** e **Windows**.

Após o build, a aplicação não exige que o usuário final possua Python ou dependências externas instaladas no sistema operacional.

---

## 🚀 Pré-requisitos e Preparação

### 1. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

---

### 2. Configurar o Ambiente de Desenvolvimento

#### No Linux (Ubuntu / Debian e derivados)
Para criar o ambiente virtual e compilar a interface gráfica, instale os pacotes de desenvolvimento necessários:

```bash
sudo apt update
sudo apt install python3-tk python3-venv python3-dev tk-dev -y
```

> **Nota:** Esses pacotes são exigidos apenas para quem vai desenvolver ou gerar o executável. O usuário final não precisa instalá-los.

#### No Windows
Certifique-se de ter o Python 3 instalado e configurado no `PATH` do sistema.

---

## 🛠️ Instalação e Build

O projeto utiliza um `Makefile` para automatizar tarefas comuns de desenvolvimento:

### 3. Criar Ambiente Virtual e Instalar Dependências

Execute no terminal:

```bash
make install
```

Este comando executa automaticamente:
* Criação do ambiente virtual Python (`.venv`)
* Atualização do gerenciador de pacotes `pip`
* Instalação de todas as bibliotecas necessárias para o projeto

---

### 4. Gerar o Executável Standalone

Para compilar o binário final:

```bash
make build
```

O executável compilado será colocado no diretório `dist/`:
* **Linux:** `dist/simulador`
* **Windows:** `dist/simulador.exe`

> **Observação:** O arquivo gerado em `dist/` contém todas as dependências e o interpretador embutidos. O usuário final pode executar diretamente sem nenhuma configuração adicional.

---

## 💻 Como Rodar o Executável

Após gerar o executável (ou ao distribuí-lo para o usuário final):

### No Linux
```bash
cd dist
./simulador
```

### No Windows
```powershell
cd dist
.\simulador.exe
```

---

## 🧹 Limpeza de Arquivos Temporários

Para remover pastas de compilação temporárias (`build/`, `dist/`), cache do Python e o ambiente virtual `.venv`:

```bash
make clean
```