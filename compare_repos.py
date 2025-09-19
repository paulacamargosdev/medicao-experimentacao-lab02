import csv
import pandas as pd

def compare_repositories():
    """Compara repositórios analisados com a lista completa"""
    
    print("📋 Carregando lista completa de repositórios...")
    all_repos_df = pd.read_csv("top_1000_java_repos_metrics.csv")
    all_repos = set(all_repos_df['full_name'].tolist())
    print(f"✅ Total de repositórios na lista: {len(all_repos)}")
    
    print("📊 Carregando repositórios já analisados...")
    try:
        analyzed_df = pd.read_csv("repository_analysis_results.csv")
        analyzed_repos = set(analyzed_df['full_name'].tolist())
        print(f"✅ Repositórios já analisados: {len(analyzed_repos)}")
    except FileNotFoundError:
        print("⚠️  Nenhum resultado de análise encontrado")
        analyzed_repos = set()
    
    remaining_repos = all_repos - analyzed_repos
    print(f"⏳ Repositórios restantes para analisar: {len(remaining_repos)}")
    
    progress = (len(analyzed_repos) / len(all_repos)) * 100
    print(f"📈 Progresso: {progress:.1f}%")
    
    remaining_list = []
    for _, row in all_repos_df.iterrows():
        if row['full_name'] in remaining_repos:
            remaining_list.append(row['full_name'])
    
    print(f"\n🎯 PRÓXIMOS 20 REPOSITÓRIOS PARA ANALISAR:")
    for i, repo in enumerate(remaining_list[:20], 1):
        stars = all_repos_df[all_repos_df['full_name'] == repo]['stars'].iloc[0]
        print(f"{i:2d}. {repo} ({stars:,} ⭐)")
    
    remaining_df = all_repos_df[all_repos_df['full_name'].isin(remaining_repos)]
    remaining_df.to_csv("remaining_repos_to_analyze.csv", index=False)
    print(f"\n💾 Lista de repositórios restantes salva em: remaining_repos_to_analyze.csv")
    
    return remaining_list

if __name__ == "__main__":
    remaining = compare_repositories()
    print(f"\n📊 RESUMO:")
    print(f"Total de repositórios: {len(remaining) + len(set(pd.read_csv('repository_analysis_results.csv')['full_name']))}")
    print(f"Já analisados: {len(set(pd.read_csv('repository_analysis_results.csv')['full_name']))}")
    print(f"Restantes: {len(remaining)}")
