import requests
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "User-Agent": "Java-Repository-Analyzer/1.0",
    "Content-Type": "application/json"
}
GRAPHQL_URL = "https://api.github.com/graphql"
MAX_RETRIES = 5
PAGE_SIZE = 50  

query = """
query ($cursor: String) {
  search(query: "language:Java sort:stars-desc", type: REPOSITORY, first: %d, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      ... on Repository {
        name
        owner { login }
        stargazerCount
        forkCount
        url
        description
        createdAt
        updatedAt
        pushedAt
        releases { totalCount }
        primaryLanguage { name }
        languages(first: 10) { edges { node { name } size } }
      }
    }
  }
}
""" % PAGE_SIZE

def run_query(query, variables):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.post(
                GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers=HEADERS,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"GraphQL errors: {data['errors']}")
                    return None
                return data
            elif response.status_code in [502, 503, 504]:
                print(f"Server error {response.status_code}, retrying in 5s...")
                time.sleep(5)
                retries += 1
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}, retrying in 5s...")
            time.sleep(5)
            retries += 1
    print("Máximo de tentativas atingido.")
    return None

def save_to_csv(repositories, filename="top_1000_java_repos_metrics.csv"):
    if not repositories:
        print("Nenhum repositório para salvar.")
        return
    
    csv_data = []
    for repo in repositories:
       
        total_bytes = sum(edge["size"] for edge in repo.get("languages", {}).get("edges", []))
        
        created_date = datetime.strptime(repo["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
        age_years = (datetime.now() - created_date).days / 365.25
        
        csv_data.append({
            "full_name": f"{repo['owner']['login']}/{repo['name']}",
            "owner": repo["owner"]["login"],
            "name": repo["name"],
            "description": repo.get("description", "") or "",
            "url": repo["url"],
            "stars": repo["stargazerCount"],
            "forks": repo["forkCount"],
            "primary_language": repo.get("primaryLanguage", {}).get("name", "Java"),
            "releases": repo.get("releases", {}).get("totalCount", 0),
            "age_years": round(age_years, 2),
            "size_bytes": total_bytes
        })
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data[0].keys())
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"Lista de {len(csv_data)} repositórios salva em {filename}")

def main():
    print("=== Coletor de Métricas de Repositórios Java ===\n")
    repos = []
    cursor = None

    while len(repos) < 1000:
        variables = {"cursor": cursor}
        result = run_query(query, variables)
        if result is None:
            print("Erro na consulta, tentando novamente em 5s...")
            time.sleep(5)
            continue
        
        nodes = result["data"]["search"]["nodes"]
        repos.extend(nodes)
        print(f"Coletados {len(repos)} repositórios até agora...")
        
        page_info = result["data"]["search"]["pageInfo"]
        if not page_info["hasNextPage"]:
            print("Não há mais páginas disponíveis.")
            break
        
        cursor = page_info["endCursor"]
        time.sleep(3)  
    
    repos = repos[:1000]  
    if repos:
        save_to_csv(repos)
        print("\nTop 5 repositórios por estrelas:")
        for i, repo in enumerate(sorted(repos, key=lambda x: x["stargazerCount"], reverse=True)[:5]):
            print(f"{i+1}. {repo['owner']['login']}/{repo['name']} - {repo['stargazerCount']} ⭐")
    else:
        print("Nenhum repositório foi coletado.")

if __name__ == "__main__":
    main()
