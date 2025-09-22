import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuração do estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Carregar os dados
df = pd.read_csv('results/repository_analysis_results.csv')

# Configurar matplotlib para português
plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)

print("=== ANÁLISE DE CARACTERÍSTICAS DE QUALIDADE DE SISTEMAS JAVA ===\n")
print(f"Total de repositórios analisados: {len(df)}")
print(f"Colunas disponíveis: {list(df.columns)}")

# Verificar dados faltantes
print(f"\nDados faltantes por coluna:")
print(df.isnull().sum())

# Estatísticas descritivas básicas
print(f"\n=== ESTATÍSTICAS DESCRITIVAS ===")
print(df.describe())

# Função para calcular correlações e gerar gráficos
def analyze_relationship(x_col, y_cols, title, xlabel):
    """Analisa a relação entre uma variável x e múltiplas variáveis y"""
    print(f"\n=== {title} ===")
    
    # Calcular correlações
    correlations = {}
    for y_col in y_cols:
        if y_col in df.columns and x_col in df.columns:
            # Remover valores NaN para cálculo de correlação
            clean_data = df[[x_col, y_col]].dropna()
            if len(clean_data) > 0:
                corr, p_value = stats.pearsonr(clean_data[x_col], clean_data[y_col])
                correlations[y_col] = {'correlation': corr, 'p_value': p_value}
                print(f"{y_col}: r = {corr:.3f}, p = {p_value:.3f}")
    
    # Criar gráficos
    n_metrics = len(y_cols)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, y_col in enumerate(y_cols):
        if i < 4 and y_col in df.columns:
            # Scatter plot
            clean_data = df[[x_col, y_col]].dropna()
            if len(clean_data) > 0:
                axes[i].scatter(clean_data[x_col], clean_data[y_col], alpha=0.6, s=30)
                
                # Linha de tendência
                z = np.polyfit(clean_data[x_col], clean_data[y_col], 1)
                p = np.poly1d(z)
                axes[i].plot(clean_data[x_col], p(clean_data[x_col]), "r--", alpha=0.8)
                
                axes[i].set_xlabel(xlabel)
                axes[i].set_ylabel(y_col.upper())
                axes[i].set_title(f'{y_col.upper()} vs {xlabel}')
                
                # Adicionar coeficiente de correlação
                if y_col in correlations:
                    corr = correlations[y_col]['correlation']
                    axes[i].text(0.05, 0.95, f'r = {corr:.3f}', 
                               transform=axes[i].transAxes, 
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'grafico_{title.lower().replace(" ", "_")}.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return correlations

# Definir métricas de qualidade
quality_metrics = ['cbo', 'dit', 'lcom', 'loc']

# RQ 01: Popularidade (stars) vs Qualidade
print("\n" + "="*60)
corr_stars = analyze_relationship('stars', quality_metrics, 
                                 'RQ 01: Popularidade vs Qualidade', 'Número de Estrelas')

# RQ 02: Maturidade (idade_anos) vs Qualidade  
print("\n" + "="*60)
corr_age = analyze_relationship('idade_anos', quality_metrics,
                               'RQ 02: Maturidade vs Qualidade', 'Idade (anos)')

# RQ 03: Atividade (releases) vs Qualidade
print("\n" + "="*60)
corr_releases = analyze_relationship('releases', quality_metrics,
                                    'RQ 03: Atividade vs Qualidade', 'Número de Releases')

# RQ 04: Tamanho (loc) vs Outras métricas de qualidade
print("\n" + "="*60)
other_metrics = ['cbo', 'dit', 'lcom']
corr_size = analyze_relationship('loc', other_metrics,
                                'RQ 04: Tamanho vs Qualidade', 'Linhas de Código (LOC)')

# Análise de distribuições
print("\n" + "="*60)
print("=== ANÁLISE DE DISTRIBUIÇÕES ===")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for i, metric in enumerate(['stars', 'idade_anos', 'releases', 'cbo', 'dit', 'lcom']):
    if metric in df.columns:
        # Histograma
        clean_data = df[metric].dropna()
        axes[i].hist(clean_data, bins=30, alpha=0.7, edgecolor='black')
        axes[i].set_title(f'Distribuição de {metric.upper()}')
        axes[i].set_xlabel(metric.upper())
        axes[i].set_ylabel('Frequência')
        
        # Adicionar estatísticas
        mean_val = clean_data.mean()
        median_val = clean_data.median()
        std_val = clean_data.std()
        axes[i].axvline(mean_val, color='red', linestyle='--', label=f'Média: {mean_val:.2f}')
        axes[i].axvline(median_val, color='green', linestyle='--', label=f'Mediana: {median_val:.2f}')
        axes[i].legend()

plt.tight_layout()
plt.savefig('distribuicoes_metricas.png', dpi=300, bbox_inches='tight')
plt.show()

# Matriz de correlação
print("\n" + "="*60)
print("=== MATRIZ DE CORRELAÇÃO ===")

# Selecionar apenas colunas numéricas relevantes
numeric_cols = ['stars', 'releases', 'idade_anos', 'cbo', 'dit', 'lcom', 'loc']
correlation_matrix = df[numeric_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
            square=True, fmt='.3f', cbar_kws={'label': 'Coeficiente de Correlação'})
plt.title('Matriz de Correlação entre Métricas')
plt.tight_layout()
plt.savefig('matriz_correlacao.png', dpi=300, bbox_inches='tight')
plt.show()

# Análise por quartis de popularidade
print("\n" + "="*60)
print("=== ANÁLISE POR QUARTIS DE POPULARIDADE ===")

# Dividir em quartis baseado no número de estrelas
df['stars_quartile'] = pd.qcut(df['stars'], q=4, labels=['Q1 (Baixa)', 'Q2 (Média-Baixa)', 'Q3 (Média-Alta)', 'Q4 (Alta)'])

fig, axes = plt.subplots(2, 2, figsize=(15, 12))
axes = axes.flatten()

for i, metric in enumerate(['cbo', 'dit', 'lcom', 'loc']):
    if metric in df.columns:
        # Box plot por quartil
        sns.boxplot(data=df, x='stars_quartile', y=metric, ax=axes[i])
        axes[i].set_title(f'{metric.upper()} por Quartil de Popularidade')
        axes[i].set_xlabel('Quartil de Popularidade')
        axes[i].set_ylabel(metric.upper())
        axes[i].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('boxplot_quartis_popularidade.png', dpi=300, bbox_inches='tight')
plt.show()

# Estatísticas por quartil
print("\nEstatísticas por quartil de popularidade:")
quartile_stats = df.groupby('stars_quartile')[quality_metrics].agg(['mean', 'median', 'std'])
print(quartile_stats)

print("\n=== ANÁLISE CONCLUÍDA ===")
