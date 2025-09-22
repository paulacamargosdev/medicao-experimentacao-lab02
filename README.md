# 📊 Análise de Características de Qualidade de Sistemas Java

Este projeto tem como foco a análise de características de qualidade de sistemas Java através de métricas de código usando a ferramenta [CK (Chidamber & Kemerer)](https://github.com/mauricioaniche/ck). A aplicação clona um repositório Java do GitHub, executa o CK Tool e exibe métricas por **classe**, **método**, **campo** e **variável**.

---

## 🧠 O que é CK?

**CK** significa *Chidamber & Kemerer* – os autores de um dos primeiros conjuntos de métricas orientadas a objetos. A ferramenta **CK** implementa e estende essas métricas para projetos Java. Ela analisa o código-fonte estático e gera arquivos `.csv` com as métricas detalhadas.

---

## 📈 Métricas extraídas e analisadas

Esta tabela contém métricas de qualidade extraídas em nível de classe, sendo fundamentais para entender o **design estrutural** de um sistema. Para o laboratório atual, foram extraídas somente:


| Coluna                   | Descrição                                                                 |
|--------------------------|---------------------------------------------------------------------------|
| file                     | Caminho do arquivo Java analisado.                                       |
| class                    | Nome totalmente qualificado da classe.                                   |
| type                     | Tipo da classe (ex: class, interface, enum).                             |
| cbo                      | Coupling Between Objects — acoplamento entre objetos.                    |
| dit                      | Depth of Inheritance Tree — profundidade na hierarquia de herança.       |
| lcom                     | Lack of Cohesion of Methods — coesão entre métodos da classe.            |
| loc                      | Lines of Code — linhas de código da classe.                              |

Também foram coletadas métricas de processo, sendo elas:

- **Popularidade**: Número de estrelas
- **Atividade**: Número de *releases*
- **Maturidade**: Idade (em anos) de cada repositório

---

## ❓ Questões de Pesquisa

- **RQ 01**: Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?
- **RQ 02**: Qual a relação entre a maturidade dos repositórios e as suas características de qualidade?
- **RQ 03**: Qual a relação entre a atividade dos repositórios e as suas características de qualidade?
- **RQ 04**: Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?

### ❔RQ 01



### ❔RQ 02



### ❔RQ 03



### ❔RQ 04

