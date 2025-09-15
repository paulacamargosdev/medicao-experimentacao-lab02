# Lab02S01 - Análise de Características de Qualidade de Sistemas Java

Este projeto tem como foco a análise de características de qualidade de sistemas Java através de métricas de código.

## Objetivo

Analisar aspectos da qualidade de repositórios desenvolvidos na linguagem Java, correlacionando-os com características do processo de desenvolvimento, utilizando métricas de produto calculadas através da ferramenta CK.

## Questões de Pesquisa

- **RQ 01**: Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?
- **RQ 02**: Qual a relação entre a maturidade dos repositórios e as suas características de qualidade?
- **RQ 03**: Qual a relação entre a atividade dos repositórios e as suas características de qualidade?
- **RQ 04**: Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?

## Métricas Analisadas

### Métricas de Processo

- **Popularidade**: Número de estrelas
- **Tamanho**: Linhas de código (LOC) e linhas de comentários
- **Atividade**: Número de releases
- **Maturidade**: Idade (em anos) de cada repositório

### Métricas de Qualidade

- **CBO**: Coupling Between Objects
- **DIT**: Depth of Inheritance Tree
- **LCOM**: Lack of Cohesion of Methods

## Arquivos do Projeto

### Scripts Principais

1. **`collect_repositories.py`**

   - Coleta os top 1000 repositórios Java mais populares do GitHub
   - Utiliza a API REST do GitHub
   - Salva resultados em CSV

### Arquivos de Configuração

- **`requirements.txt`**: Dependências Python necessárias
- **`README.md`**: Documentação do projeto

## Instalação e Uso

### Pré-requisitos

- Python 3.7+
- Git
- Acesso à internet

### Instalação

1. Clone ou baixe os arquivos do projeto
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Uso

#### 1. Coletar Lista de Repositórios

```bash
python collect_repositories.py
```

Este script tem como objetivo:

- Buscar os 1000 repositórios Java mais populares
- Salvar a lista em `top_1000_java_repos.csv`

#### 2. Analisar Repositório Individual

```bash
python analyze_single_repo.py
```

Este script irá:

- Clonar o repositório Spring Boot
- Executar análise com CK
- Gerar CSV com métricas detalhadas

#### 3. Automação Completa

```bash
python automation_script.py
```

Este script irá:

- Carregar lista de repositórios
- Clonar e analisar múltiplos repositórios
- Gerar relatório consolidado

## Estrutura de Saída

### Arquivos CSV Gerados

1. **`top_1000_java_repos.csv`**

   - Lista completa dos repositórios coletados
   - Contém informações básicas (estrelas, forks, tamanho, etc.)

## Exemplo de Resultados
//todo: fix
