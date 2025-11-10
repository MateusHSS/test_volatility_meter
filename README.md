# Analisador de Volatilidade de Testes

Este script em Python foi projetado para analisar repositórios Git, identificar arquivos de teste e calcular a frequência com que cada arquivo foi modificado ao longo do histórico do projeto.

O objetivo é medir a "volatilidade dos testes" — um indicador de quantos recursos de manutenção estão sendo dedicados aos testes, em vez de ao código-fonte principal. Um número elevado de modificações em arquivos de teste pode indicar testes frágeis, requisitos instáveis ou débitos técnicos.

## Pré-requisitos

Antes de executar o script, você precisa ter dois softwares instalados em seu sistema:

1. Python 3.6+: Você pode baixar a versão mais recente em [python.org](python.org).

2. Git: O script depende de comandos Git para clonar e analisar os repositórios. Você pode baixá-lo em [git-scm.com/downloads](git-scm.com/downloads).

## Instalação

O script depende de uma biblioteca Python chamada ``pydriller``. Você pode instalá-la usando o ``pip`` (gerenciador de pacotes do Python).

1. Abra seu terminal ou Prompt de Comando.

2. Execute o seguinte comando para instalar o ``pydriller``:
    
```bash
    pip install pydriller
```

## Como Usar

Siga estes passos para executar a análise:

### 1. Clone o repositório

Clone o repositório no local desejado:

```bash
git clone https://github.com/MateusHSS/test_volatility_meter
```

### 2. Crie um Arquivo de Repositórios

Na mesma pasta onde você clonou o repositório, crie um arquivo de texto. Você pode chamá-lo, por exemplo, ``repos.txt``.

Dentro deste arquivo, liste as URLs completas dos repositórios Git que você deseja analisar, um repositório por linha.

Exemplo de ``repos.txt``:

```txt
https://github.com/django/django
https://github.com/pallets/flask
https://github.com/fastapi/fastapi
```

### 3. Execute o Script

O script é executado a partir da linha de comando e recebe dois argumentos:

  1. Linguagem: O tipo de arquivo de teste a ser procurado (``py``, ``js``, ou ``ts``).

  2. Arquivo de Lista: O nome do arquivo de texto que você criou (ex: ``repos.txt``).

Abra seu terminal ou Prompt de Comando, navegue até a pasta onde o script está salvo e execute o seguinte comando:

```bash
python main.py [linguagem] [arquivo_de_repositorios]
```

Exemplo prático (para Python):

```bash
python main.py py repos.txt
```

Exemplo prático (para TypeScript):

```bash
python main.py ts repos.txt
```

### 4. Entendendo o Processo

Quando você executa o script, ele fará o seguinte:

  1. Criará uma pasta chamada ``temp_repos/`` para clonar temporariamente os repositórios.

  2. Processará cada repositório da sua lista, um por um.

  3. Contará o número de commits que modificaram cada arquivo de teste (baseado no tipo de linguagem que você especificou).

  4. Limpará o repositório baixado de ``temp_repos/`` após a conclusão para economizar espaço.


### 5. Saída (Resultados)

O script criará um novo diretório chamado ``results/`` no mesmo local.

Dentro desta pasta, você encontrará um arquivo ``.csv`` para cada repositório analisado, nomeado após o projeto (ex: ``django.csv``, ``flask.csv``, etc.).

Cada arquivo CSV conterá duas colunas:

- **file**: O caminho completo para o arquivo de teste dentro do repositório.

- **modifications**: O número total de vezes que esse arquivo foi modificado na história do projeto.