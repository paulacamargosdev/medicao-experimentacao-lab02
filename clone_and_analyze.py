import os
import csv
import subprocess
import shutil
import time
from pathlib import Path
from git import Repo
import pandas as pd
import stat

class RepositoryAnalyzer:
    def __init__(self,
                 repos_csv_file="top_1000_java_repos_metrics.csv",
                 clone_dir="repositories",
                 ck_jar_path=r"C:\Users\gabri\Downloads\ck-ck-0.7.0\ck-ck-0.7.0\target\ck-0.7.0-jar-with-dependencies.jar"):
        self.repos_csv_file = repos_csv_file
        self.clone_dir = Path(clone_dir)
        self.clone_dir.mkdir(exist_ok=True)
        self.results = []

        self.ck_jar_path = Path(ck_jar_path)

    def handle_remove_readonly(self, func, path, exc_info):
        """Força a remoção de arquivos somente leitura no Windows"""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def load_repositories(self):
        """Carrega a lista de repositórios do arquivo CSV"""
        if not os.path.exists(self.repos_csv_file):
            print(f"Arquivo {self.repos_csv_file} não encontrado.")
            return []

        repos = []
        with open(self.repos_csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                repos.append(row)

        print(f"Carregados {len(repos)} repositórios do arquivo CSV")
        return repos

    def clone_repository(self, repo_url, repo_name):
        """Clona um repositório específico"""
        repo_path = self.clone_dir / repo_name

        if repo_path.exists():
            shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)

        try:
            print(f"Clonando {repo_name}...")
            Repo.clone_from(repo_url, repo_path, depth=1)
            print(f"✓ {repo_name} clonado com sucesso")
            return repo_path
        except Exception as e:
            print(f"✗ Erro ao clonar {repo_name}: {e}")
            return None

    def install_ck_tool(self):
        """Verifica se o ck.jar está disponível"""
        if self.ck_jar_path.exists():
            print(f"✓ CK encontrado em {self.ck_jar_path}")
            return True
        else:
            print(f"✗ ck.jar não encontrado em {self.ck_jar_path}")
            return False

    def analyze_repository_with_ck(self, repo_path):
        """Analisa um repositório usando a ferramenta CK"""
        if not repo_path or not repo_path.exists():
            return None

        try:
            print(f"Analisando {repo_path.name} com CK...")

            ck_output = repo_path / "ck_results.csv"
            src_path = repo_path / "src"
            if not src_path.exists():
                src_path = repo_path

            result = subprocess.run(
                ["java", "-jar", str(self.ck_jar_path),
                 str(src_path.resolve()), "true", "0", "false", str(ck_output.resolve())],
                capture_output=True, text=True, timeout=600,
                cwd=str(repo_path.resolve())
            )

            if not ck_output.exists() or ck_output.stat().st_size == 0:
                with open(ck_output, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                print(f"⚠ CK não gerou CSV válido, mas salvamos stdout em {ck_output}")

            print(f"✓ Análise CK concluída para {repo_path.name}")
            return self.parse_ck_results(repo_path)

        except subprocess.TimeoutExpired:
            print(f"✗ Timeout na análise CK para {repo_path.name}")
            return None
        except Exception as e:
            print(f"✗ Erro inesperado na análise CK para {repo_path.name}: {e}")
            return None

    def parse_ck_results(self, repo_path):
        """Processa os resultados do CK e retorna métricas sumarizadas"""
        ck_file = repo_path / "ck_results.csv"

        if not ck_file.exists():
            print(f"Arquivo de resultados CK não encontrado: {ck_file}")
            return None

        try:
            try:
                df = pd.read_csv(ck_file)
            except pd.errors.ParserError:
                with open(ck_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                data = []
                for line in lines:
                    parts = line.strip().split(",")
                    if len(parts) >= 5 and parts[1].isdigit():
                        data.append({
                            "class": parts[0],
                            "cbo": int(parts[1]),
                            "dit": int(parts[2]),
                            "lcom": int(parts[3]),
                            "loc": int(parts[4])
                        })
                if not data:
                    print(f"Nenhuma métrica encontrada para {repo_path.name}")
                    return None
                df = pd.DataFrame(data)

            metrics = {
                "repository": repo_path.name,
                "total_classes": len(df),
                "avg_cbo": df["cbo"].mean() if "cbo" in df.columns else 0,
                "median_cbo": df["cbo"].median() if "cbo" in df.columns else 0,
                "std_cbo": df["cbo"].std() if "cbo" in df.columns else 0,
                "avg_dit": df["dit"].mean() if "dit" in df.columns else 0,
                "median_dit": df["dit"].median() if "dit" in df.columns else 0,
                "std_dit": df["dit"].std() if "dit" in df.columns else 0,
                "avg_lcom": df["lcom"].mean() if "lcom" in df.columns else 0,
                "median_lcom": df["lcom"].median() if "lcom" in df.columns else 0,
                "std_lcom": df["lcom"].std() if "lcom" in df.columns else 0,
                "total_loc": df["loc"].sum() if "loc" in df.columns else 0,
                "avg_loc_per_class": df["loc"].mean() if "loc" in df.columns else 0,
                "max_cbo": df["cbo"].max() if "cbo" in df.columns else 0,
                "max_dit": df["dit"].max() if "dit" in df.columns else 0,
                "max_lcom": df["lcom"].max() if "lcom" in df.columns else 0,
            }

            print(f"✓ Métricas processadas para {repo_path.name}: {metrics['total_classes']} classes")
            return metrics

        except Exception as e:
            print(f"✗ Erro ao processar resultados CK para {repo_path.name}: {e}")
            return None

    def analyze_single_repository(self, repo_info):
        repo_name = repo_info["full_name"].replace("/", "_")
        repo_url = f"https://github.com/{repo_info['full_name']}.git"

        print(f"\n=== Analisando {repo_info['full_name']} ===")
        print(f"Estrelas: {repo_info['stars']}")
        print(f"Forks: {repo_info['forks']}")
        print(f"Idade: {repo_info['age_years']} anos")
        print(f"Releases: {repo_info['releases']}")

        repo_path = self.clone_repository(repo_url, repo_name)
        if not repo_path:
            return None

        ck_metrics = self.analyze_repository_with_ck(repo_path)
        if not ck_metrics:
            shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)
            return None

        combined_metrics = {**repo_info, **ck_metrics}

        shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)
        print(f"✓ Repositório {repo_name} removido após análise")

        return combined_metrics

    def save_results(self, results, filename="repository_analysis_results.csv"):
        if not results:
            print("Nenhum resultado para salvar")
            return

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"✓ Resultados salvos em {filename}")
        print(f"Total de repositórios analisados: {len(results)}")

    def run_analysis(self, num_repos=1):
        print("=== Analisador de Repositórios Java com CK ===\n")

        if not self.install_ck_tool():
            print("Não foi possível encontrar o ck.jar. Abortando.")
            return

        repos = self.load_repositories()
        if not repos:
            return

        repos_to_analyze = repos[:num_repos]
        print(f"\nAnalisando {len(repos_to_analyze)} repositórios...")

        for i, repo_info in enumerate(repos_to_analyze, 1):
            print(f"\n[{i}/{len(repos_to_analyze)}] Processando...")
            result = self.analyze_single_repository(repo_info)
            if result:
                self.results.append(result)
                print(f"✓ Repositório {i} analisado com sucesso")
            else:
                print(f"✗ Falha na análise do repositório {i}")

            if i < len(repos_to_analyze):
                print("Aguardando 5 segundos...")
                time.sleep(5)

        if self.results:
            self.save_results(self.results)
            self.print_summary()
        else:
            print("Nenhum repositório foi analisado com sucesso.")

    def print_summary(self):
        if not self.results:
            return

        print("\n=== RESUMO DOS RESULTADOS ===")

        total_repos = len(self.results)
        total_classes = sum(r["total_classes"] for r in self.results)
        total_loc = sum(r["total_loc"] for r in self.results)

        print(f"Repositórios analisados: {total_repos}")
        print(f"Total de classes: {total_classes}")
        print(f"Total de linhas de código: {total_loc:,}")

        avg_cbo = sum(r["avg_cbo"] for r in self.results) / total_repos
        avg_dit = sum(r["avg_dit"] for r in self.results) / total_repos
        avg_lcom = sum(r["avg_lcom"] for r in self.results) / total_repos

        print(f"\nMétricas de Qualidade Médias:")
        print(f"CBO médio: {avg_cbo:.2f}")
        print(f"DIT médio: {avg_dit:.2f}")
        print(f"LCOM médio: {avg_lcom:.2f}")

        print(f"\nTop 3 repositórios por estrelas:")
        sorted_repos = sorted(self.results, key=lambda x: int(x["stars"]), reverse=True)
        for i, repo in enumerate(sorted_repos[:3], 1):
            print(f"{i}. {repo['full_name']} - {repo['stars']} ⭐ (CBO: {repo['avg_cbo']:.2f})")

def main():
    analyzer = RepositoryAnalyzer()
    print("Executando análise (1 repositório)...")
    analyzer.run_analysis(num_repos=3)

if __name__ == "__main__":
    main()
