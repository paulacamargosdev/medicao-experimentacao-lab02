import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuração
plt.rcParams['font.size'] = 12
plt.rcParams['figure.figsize'] = (15, 10)
sns.set_style("whitegrid")
sns.set_palette("Set2")

# Carregar dados
df = pd.read_csv('results/repository_analysis_results.csv')

# Configurar matplotlib para português
plt.rcParams['font.family'] = 'DejaVu Sans'

print("Gerando gráficos detalhados para cada questão de pesquisa...")

# 1. RQ 01: Popularidade vs Qualidade - Gráfico detalhado
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('RQ 01: Relação entre Popularidade (Estrelas) e Características de Qualidade', fontsize=16, fontweight='bold')

metrics = ['cbo', 'dit', 'lcom', 'loc']
titles = ['Acoplamento (CBO)', 'Profundidade de Herança (DIT)', 'Falta de Coesão (LCOM)', 'Linhas de Código (LOC)']

for i, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[i//2, i%2]
    
    # Scatter plot com linha de tendência
    clean_data = df[['stars', metric]].dropna()
    if len(clean_data) > 0:
        # Usar log para stars para melhor visualização
        clean_data['log_stars'] = np.log10(clean_data['stars'])
        
        ax.scatter(clean_data['log_stars'], clean_data[metric], alpha=0.6, s=20)
        
        # Linha de tendência
        z = np.polyfit(clean_data['log_stars'], clean_data[metric], 1)
        p = np.poly1d(z)
        ax.plot(clean_data['log_stars'], p(clean_data['log_stars']), "r--", alpha=0.8, linewidth=2)
        
        # Calcular correlação
        corr, p_val = stats.pearsonr(clean_data['log_stars'], clean_data[metric])
        
        ax.set_xlabel('Log10(Número de Estrelas)')
        ax.set_ylabel(title)
        ax.set_title(f'{title}\nCorrelação: r = {corr:.3f} (p = {p_val:.3f})')
        
        # Adicionar grid
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('RQ01_Popularidade_vs_Qualidade.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. RQ 02: Maturidade vs Qualidade
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('RQ 02: Relação entre Maturidade (Idade) e Características de Qualidade', fontsize=16, fontweight='bold')

for i, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[i//2, i%2]
    
    clean_data = df[['idade_anos', metric]].dropna()
    if len(clean_data) > 0:
        ax.scatter(clean_data['idade_anos'], clean_data[metric], alpha=0.6, s=20)
        
        # Linha de tendência
        z = np.polyfit(clean_data['idade_anos'], clean_data[metric], 1)
        p = np.poly1d(z)
        ax.plot(clean_data['idade_anos'], p(clean_data['idade_anos']), "r--", alpha=0.8, linewidth=2)
        
        # Calcular correlação
        corr, p_val = stats.pearsonr(clean_data['idade_anos'], clean_data[metric])
        
        ax.set_xlabel('Idade do Repositório (anos)')
        ax.set_ylabel(title)
        ax.set_title(f'{title}\nCorrelação: r = {corr:.3f} (p = {p_val:.3f})')
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('RQ02_Maturidade_vs_Qualidade.png', dpi=300, bbox_inches='tight')
plt.show()

# 3. RQ 03: Atividade vs Qualidade
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('RQ 03: Relação entre Atividade (Releases) e Características de Qualidade', fontsize=16, fontweight='bold')

for i, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[i//2, i%2]
    
    clean_data = df[['releases', metric]].dropna()
    if len(clean_data) > 0:
        ax.scatter(clean_data['releases'], clean_data[metric], alpha=0.6, s=20)
        
        # Linha de tendência
        z = np.polyfit(clean_data['releases'], clean_data[metric], 1)
        p = np.poly1d(z)
        ax.plot(clean_data['releases'], p(clean_data['releases']), "r--", alpha=0.8, linewidth=2)
        
        # Calcular correlação
        corr, p_val = stats.pearsonr(clean_data['releases'], clean_data[metric])
        
        ax.set_xlabel('Número de Releases')
        ax.set_ylabel(title)
        ax.set_title(f'{title}\nCorrelação: r = {corr:.3f} (p = {p_val:.3f})')
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('RQ03_Atividade_vs_Qualidade.png', dpi=300, bbox_inches='tight')
plt.show()

# 4. RQ 04: Tamanho vs Qualidade (excluindo LOC)
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('RQ 04: Relação entre Tamanho (LOC) e Outras Características de Qualidade', fontsize=16, fontweight='bold')

size_metrics = ['cbo', 'dit', 'lcom']
size_titles = ['Acoplamento (CBO)', 'Profundidade de Herança (DIT)', 'Falta de Coesão (LCOM)']

for i, (metric, title) in enumerate(zip(size_metrics, size_titles)):
    ax = axes[i]
    
    clean_data = df[['loc', metric]].dropna()
    if len(clean_data) > 0:
        ax.scatter(clean_data['loc'], clean_data[metric], alpha=0.6, s=20)
        
        # Linha de tendência
        z = np.polyfit(clean_data['loc'], clean_data[metric], 1)
        p = np.poly1d(z)
        ax.plot(clean_data['loc'], p(clean_data['loc']), "r--", alpha=0.8, linewidth=2)
        
        # Calcular correlação
        corr, p_val = stats.pearsonr(clean_data['loc'], clean_data[metric])
        
        ax.set_xlabel('Linhas de Código (LOC)')
        ax.set_ylabel(title)
        ax.set_title(f'{title}\nCorrelação: r = {corr:.3f} (p = {p_val:.3f})')
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('RQ04_Tamanho_vs_Qualidade.png', dpi=300, bbox_inches='tight')
plt.show()

# 5. Análise por quartis de popularidade - Box plots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Distribuição das Métricas de Qualidade por Quartil de Popularidade', fontsize=16, fontweight='bold')

# Criar quartis
df['stars_quartile'] = pd.qcut(df['stars'], q=4, labels=['Q1 (Baixa)', 'Q2 (Média-Baixa)', 'Q3 (Média-Alta)', 'Q4 (Alta)'])

for i, (metric, title) in enumerate(zip(metrics, titles)):
    ax = axes[i//2, i%2]
    
    # Box plot
    sns.boxplot(data=df, x='stars_quartile', y=metric, ax=ax)
    ax.set_title(f'{title} por Quartil de Popularidade')
    ax.set_xlabel('Quartil de Popularidade')
    ax.set_ylabel(title)
    ax.tick_params(axis='x', rotation=45)
    
    # Adicionar estatísticas
    quartile_stats = df.groupby('stars_quartile')[metric].agg(['mean', 'median'])
    for j, (quartile, stats_row) in enumerate(quartile_stats.iterrows()):
        ax.text(j, ax.get_ylim()[1] * 0.95, f'Média: {stats_row["mean"]:.1f}\nMediana: {stats_row["median"]:.1f}', 
                ha='center', va='top', fontsize=8, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

plt.tight_layout()
plt.savefig('Boxplot_Quartis_Popularidade.png', dpi=300, bbox_inches='tight')
plt.show()

# 6. Matriz de correlação com heatmap melhorado
plt.figure(figsize=(12, 10))

# Selecionar colunas numéricas
numeric_cols = ['stars', 'releases', 'idade_anos', 'cbo', 'dit', 'lcom', 'loc']
correlation_matrix = df[numeric_cols].corr()

# Criar máscara para mostrar apenas metade da matriz
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

# Heatmap
sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
            square=True, fmt='.3f', cbar_kws={'label': 'Coeficiente de Correlação'},
            linewidths=0.5)

plt.title('Matriz de Correlação entre Métricas de Processo e Qualidade', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('Matriz_Correlacao_Completa.png', dpi=300, bbox_inches='tight')
plt.show()

# 7. Gráfico de distribuições das métricas principais
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle('Distribuições das Métricas de Processo e Qualidade', fontsize=16, fontweight='bold')

all_metrics = ['stars', 'releases', 'idade_anos', 'cbo', 'dit', 'lcom', 'loc']
all_titles = ['Estrelas', 'Releases', 'Idade (anos)', 'CBO', 'DIT', 'LCOM', 'LOC']

for i, (metric, title) in enumerate(zip(all_metrics, all_titles)):
    ax = axes[i//4, i%4]
    
    clean_data = df[metric].dropna()
    
    # Histograma
    ax.hist(clean_data, bins=30, alpha=0.7, edgecolor='black', color=sns.color_palette("Set2")[i%8])
    
    # Estatísticas
    mean_val = clean_data.mean()
    median_val = clean_data.median()
    std_val = clean_data.std()
    
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Média: {mean_val:.1f}')
    ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Mediana: {median_val:.1f}')
    
    ax.set_title(f'{title}\n(σ = {std_val:.1f})')
    ax.set_xlabel(title)
    ax.set_ylabel('Frequência')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

# Remover subplot vazio
axes[1, 3].remove()

plt.tight_layout()
plt.savefig('Distribuicoes_Todas_Metricas.png', dpi=300, bbox_inches='tight')
plt.show()

print("Todos os gráficos foram gerados e salvos com sucesso!")
print("\nGráficos criados:")
print("1. RQ01_Popularidade_vs_Qualidade.png")
print("2. RQ02_Maturidade_vs_Qualidade.png") 
print("3. RQ03_Atividade_vs_Qualidade.png")
print("4. RQ04_Tamanho_vs_Qualidade.png")
print("5. Boxplot_Quartis_Popularidade.png")
print("6. Matriz_Correlacao_Completa.png")
print("7. Distribuicoes_Todas_Metricas.png")
