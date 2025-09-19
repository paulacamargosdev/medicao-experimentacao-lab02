import os
import csv
import subprocess
import shutil
import time
from pathlib import Path
from git import Repo
import pandas as pd
import stat
import concurrent.futures
from datetime import datetime
import threading

class RepositoryAnalyzer:
    def __init__(self,
                 repos_csv_file="top_1000_java_repos_metrics.csv",
                 clone_dir="repositories",
                 ck_jar_path=r"Z:\ws-PUC\lab-exp-med\ck\target\ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar",
                 results_file="repository_analysis_results.csv"):
        self.repos_csv_file = repos_csv_file
        self.clone_dir = Path(clone_dir)
        self.clone_dir.mkdir(exist_ok=True)
        self.results = []
        self.results_file = results_file
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
    
    def get_remaining_repositories(self, num_repos=100):
        """Retorna repositórios que ainda não foram analisados"""
        all_repos = self.load_repositories()
        
        analyzed_repos = set()
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    analyzed_repos = {row['full_name'] for row in reader}
                print(f"✅ {len(analyzed_repos)} repositórios já analisados")
            except Exception as e:
                print(f"⚠️ Erro ao carregar resultados existentes: {e}")
        
        remaining_repos = []
        for repo in all_repos:
            if repo['full_name'] not in analyzed_repos:
                remaining_repos.append(repo)
        
        print(f"⏳ {len(remaining_repos)} repositórios restantes para analisar")
        
        return remaining_repos[:num_repos]

    def clone_repository(self, repo_url, repo_name):
        """Clona um repositório específico"""
        repo_path = self.clone_dir / repo_name

        if repo_path.exists():
            shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)

        try:
            print(f"Clonando {repo_name}...")

            Repo.clone_from(repo_url, repo_path, depth=1, single_branch=True)
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

    def _calculate_timeout(self, repo_path):
        """Calcula timeout dinâmico baseado no tamanho do repositório"""
        try:

            java_files = list(repo_path.rglob("*.java"))
            num_java_files = len(java_files)
            

            if num_java_files < 50:
                return 60   
            elif num_java_files < 200:
                return 120  
            elif num_java_files < 500:
                return 300 
            elif num_java_files < 1000:
                return 600 
            else:
                return 900 
        except:
            return 180 

    def analyze_repository_with_ck(self, repo_path):
        """Analisa um repositório usando a ferramenta CK"""
        if not repo_path or not repo_path.exists():
            return None

        try:
            print(f"Analisando {repo_path.name} com CK...")

            ck_output = repo_path / "ck_results.csv"
            ck_class_output = repo_path / "ck_results.csvclass.csv"
            src_path = repo_path / "src"
            if not src_path.exists():
                src_path = repo_path


            timeout = self._calculate_timeout(repo_path)
            
            result = subprocess.run(
                ["java", "-jar", str(self.ck_jar_path),
                 str(src_path.resolve()), "true", "0", "false", str(ck_output.resolve())],
                capture_output=True, text=True, timeout=timeout,
                cwd=str(repo_path.resolve())
            )


            if not ck_class_output.exists() or ck_class_output.stat().st_size == 0:
                with open(ck_output, "w", encoding="utf-8") as f:
                    f.write(result.stdout)
                print(f"⚠ CK não gerou CSV válido, mas salvamos stdout em {ck_output}")
            else:
                print(f"✓ CK gerou arquivo de métricas: {ck_class_output}")

            print(f"✓ Análise CK concluída para {repo_path.name}")
            return self.parse_ck_results(repo_path)

        except subprocess.TimeoutExpired:
            print(f"✗ Timeout na análise CK para {repo_path.name} (timeout: {timeout}s)")
            return None
        except Exception as e:
            print(f"✗ Erro inesperado na análise CK para {repo_path.name}: {e}")
            return None

    def parse_ck_results(self, repo_path):
        """Processa os resultados do CK e retorna métricas sumarizadas"""
        ck_file = repo_path / "ck_results.csvclass.csv"

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

    def create_failure_metrics(self, repo_info, error_type="failure"):
        """Cria métricas de falha para repositórios que não puderam ser analisados"""
        return {
            **repo_info,
            "repository": repo_info["full_name"].replace("/", "_"),
            "total_classes": 0,
            "avg_cbo": 0,
            "median_cbo": 0,
            "std_cbo": 0,
            "avg_dit": 0,
            "median_dit": 0,
            "std_dit": 0,
            "avg_lcom": 0,
            "median_lcom": 0,
            "std_lcom": 0,
            "total_loc": 0,
            "avg_loc_per_class": 0,
            "max_cbo": 0,
            "max_dit": 0,
            "max_lcom": 0,
            "analysis_status": error_type
        }

    def analyze_single_repository(self, repo_info):
        repo_name = repo_info["full_name"].replace("/", "_")
        repo_url = f"https://github.com/{repo_info['full_name']}.git"

        print(f"\n=== Analisando {repo_info['full_name']} ===")
        print(f"Estrelas: {repo_info['stars']}")
        print(f"Forks: {repo_info['forks']}")
        print(f"Idade: {repo_info['age_years']} anos")
        print(f"Releases: {repo_info['releases']}")

        try:
            repo_path = self.clone_repository(repo_url, repo_name)
            if not repo_path:
                print(f"✗ Falha no clone de {repo_info['full_name']}")
                return self.create_failure_metrics(repo_info, "clone_failed")

            ck_metrics = self.analyze_repository_with_ck(repo_path)
            if not ck_metrics:
                print(f"✗ Falha na análise CK de {repo_info['full_name']}")
                # Limpar repositório se existir
                if repo_path and repo_path.exists():
                    shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)
                return self.create_failure_metrics(repo_info, "ck_analysis_failed")

            combined_metrics = {**repo_info, **ck_metrics}
            combined_metrics["analysis_status"] = "success"

            # Limpeza assíncrona
            def cleanup_repo():
                try:
                    if repo_path and repo_path.exists():
                        shutil.rmtree(repo_path, onerror=self.handle_remove_readonly)
                        print(f"✓ Repositório {repo_name} removido após análise")
                except Exception as e:
                    print(f"⚠ Erro ao remover {repo_name}: {e}")
            
            cleanup_thread = threading.Thread(target=cleanup_repo)
            cleanup_thread.daemon = True
            cleanup_thread.start()

            return combined_metrics

        except Exception as e:
            print(f"✗ Erro inesperado em {repo_info['full_name']}: {e}")
            return self.create_failure_metrics(repo_info, f"error: {str(e)[:50]}")

    def save_results(self, results=None, filename=None):
        """Salva resultados no arquivo CSV"""
        if results is None:
            results = self.results
        if filename is None:
            filename = self.results_file
            
        if not results:
            print("Nenhum resultado para salvar")
            return

        file_exists = os.path.exists(filename)
        
        existing_results = []
        if file_exists:
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    existing_results = list(reader)
                print(f"📂 Carregados {len(existing_results)} resultados existentes")
            except Exception as e:
                print(f"⚠️ Erro ao carregar resultados existentes: {e}")
        
        all_results = existing_results + results
        
        with open(filename, "w", newline="", encoding="utf-8") as file:
            if all_results:
                writer = csv.DictWriter(file, fieldnames=all_results[0].keys())
                writer.writeheader()
                writer.writerows(all_results)

        print(f"💾 Resultados salvos em {filename}")
        print(f"📊 Total de repositórios no arquivo: {len(all_results)}")
        print(f"🆕 Novos resultados adicionados: {len(results)}")
    
    def save_incremental(self, new_result):
        """Salva um novo resultado incrementalmente"""
        existing_results = []
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    existing_results = list(reader)
            except Exception as e:
                print(f"⚠️ Erro ao carregar resultados existentes: {e}")
        
        # Garantir que todos os campos estejam presentes
        all_results = existing_results + [new_result]
        
        # Obter todos os campos únicos de todos os resultados
        all_fieldnames = set()
        for result in all_results:
            all_fieldnames.update(result.keys())
        all_fieldnames = sorted(list(all_fieldnames))
        
        # Garantir que todos os resultados tenham todos os campos
        for result in all_results:
            for field in all_fieldnames:
                if field not in result:
                    result[field] = ""  # Valor padrão para campos ausentes
        
        with open(self.results_file, "w", newline="", encoding="utf-8") as file:
            if all_results:
                writer = csv.DictWriter(file, fieldnames=all_fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
        
        print(f"💾 Resultado incremental salvo: {new_result['full_name']}")
        print(f"📊 Total no arquivo: {len(all_results)} repositórios")

    def run_analysis(self, num_repos=100, max_workers=3):
        print("=== Analisador de Repositórios Java com CK ===\n")
        start_time = datetime.now()

        if not self.install_ck_tool():
            print("Não foi possível encontrar o ck.jar. Abortando.")
            return

        repos_to_analyze = self.get_remaining_repositories(num_repos)
        if not repos_to_analyze:
            print("✅ Todos os repositórios já foram analisados!")
            return

        print(f"\nAnalisando {len(repos_to_analyze)} repositórios restantes...")
        print(f"Usando {max_workers} workers paralelos")
        print(f"Início: {start_time.strftime('%H:%M:%S')}")


        results_lock = threading.Lock()
        
        def analyze_with_lock(repo_info, index):
            result = self.analyze_single_repository(repo_info)
            # Sempre salvar o resultado, mesmo se for falha
            if result:
                with results_lock:
                    self.results.append(result)
                    self.save_incremental(result)
                
                # Verificar se foi sucesso ou falha
                if result.get("analysis_status") == "success":
                    return True, index, repo_info['full_name']
                else:
                    return False, index, repo_info['full_name']
            else:
                # Se não retornou nada, criar métricas de falha
                failure_result = self.create_failure_metrics(repo_info, "unknown_error")
                with results_lock:
                    self.results.append(failure_result)
                    self.save_incremental(failure_result)
                return False, index, repo_info['full_name']


        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

            future_to_repo = {
                executor.submit(analyze_with_lock, repo_info, i): (i, repo_info)
                for i, repo_info in enumerate(repos_to_analyze, 1)
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_repo):
                i, repo_info = future_to_repo[future]
                completed += 1
                
                try:
                    success, index, repo_name = future.result()
                    if success:
                        print(f"✓ [{completed}/{len(repos_to_analyze)}] {repo_name} analisado com sucesso")
                    else:
                        print(f"✗ [{completed}/{len(repos_to_analyze)}] Falha na análise de {repo_name}")
                except Exception as e:
                    print(f"✗ [{completed}/{len(repos_to_analyze)}] Erro inesperado em {repo_info['full_name']}: {e}")
                

                if completed % 5 == 0:
                    elapsed = datetime.now() - start_time
                    print(f"\n📊 Progresso: {completed}/{len(repos_to_analyze)} ({completed/len(repos_to_analyze)*100:.1f}%)")
                    print(f"⏱️ Tempo decorrido: {elapsed}")
                    if completed > 0:
                        avg_time = elapsed / completed
                        remaining = (len(repos_to_analyze) - completed) * avg_time
                        print(f"⏳ Tempo estimado restante: {remaining}")
                    print()

        end_time = datetime.now()
        total_time = end_time - start_time
        print(f"\n🏁 Análise concluída em {total_time}")

        if self.results:
            self.print_summary()
        else:
            print("Nenhum repositório foi analisado com sucesso.")

    def print_summary(self):
        if not self.results:
            return

        print("\n=== RESUMO DOS RESULTADOS ===")

        total_repos = len(self.results)
        successful_repos = [r for r in self.results if r.get("analysis_status") == "success"]
        failed_repos = [r for r in self.results if r.get("analysis_status") != "success"]
        
        print(f"Total de repositórios processados: {total_repos}")
        print(f"✅ Sucessos: {len(successful_repos)}")
        print(f"❌ Falhas: {len(failed_repos)}")

        if successful_repos:
            total_classes = sum(r["total_classes"] for r in successful_repos)
            total_loc = sum(r["total_loc"] for r in successful_repos)

            print(f"\n📊 Métricas dos repositórios com sucesso:")
            print(f"Total de classes: {total_classes}")
            print(f"Total de linhas de código: {total_loc:,}")

            avg_cbo = sum(r["avg_cbo"] for r in successful_repos) / len(successful_repos)
            avg_dit = sum(r["avg_dit"] for r in successful_repos) / len(successful_repos)
            avg_lcom = sum(r["avg_lcom"] for r in successful_repos) / len(successful_repos)

            print(f"\nMétricas de Qualidade Médias:")
            print(f"CBO médio: {avg_cbo:.2f}")
            print(f"DIT médio: {avg_dit:.2f}")
            print(f"LCOM médio: {avg_lcom:.2f}")

            print(f"\nTop 3 repositórios por estrelas:")
            sorted_repos = sorted(successful_repos, key=lambda x: int(x["stars"]), reverse=True)
            for i, repo in enumerate(sorted_repos[:3], 1):
                print(f"{i}. {repo['full_name']} - {repo['stars']} ⭐ (CBO: {repo['avg_cbo']:.2f})")

        if failed_repos:
            print(f"\n❌ Repositórios com falha:")
            failure_types = {}
            for repo in failed_repos:
                status = repo.get("analysis_status", "unknown")
                failure_types[status] = failure_types.get(status, 0) + 1
            
            for failure_type, count in failure_types.items():
                print(f"  - {failure_type}: {count} repositórios")

def main():
    analyzer = RepositoryAnalyzer()
    
    print("🚀 ANALISADOR DE REPOSITÓRIOS JAVA COM CK")
    print("=" * 50)
    
    all_repos = analyzer.load_repositories()
    analyzed_repos = set()
    if os.path.exists(analyzer.results_file):
        try:
            with open(analyzer.results_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                analyzed_repos = {row['full_name'] for row in reader}
        except Exception as e:
            print(f"⚠️ Erro ao carregar resultados: {e}")
    
    total_repos = len(all_repos)
    analyzed_count = len(analyzed_repos)
    remaining_count = total_repos - analyzed_count
    progress = (analyzed_count / total_repos) * 100
    
    print("📊 STATUS DA ANÁLISE:")
    print(f"📋 Total de repositórios: {total_repos}")
    print(f"✅ Já analisados: {analyzed_count}")
    print(f"⏳ Restantes: {remaining_count}")
    print(f"📈 Progresso: {progress:.1f}%")
    
    if remaining_count == 0:
        print("🎉 Todos os repositórios já foram analisados!")
        return
    
    remaining_repos = analyzer.get_remaining_repositories(10)
    print(f"\n🎯 PRÓXIMOS 10 REPOSITÓRIOS:")
    for i, repo in enumerate(remaining_repos, 1):
        stars = repo.get('stars', 'N/A')
        print(f"{i:2d}. {repo['full_name']} ({stars} ⭐)")
    
    print(f"\n🔄 Iniciando análise dos próximos 100 repositórios...")
    print("💡 Dica: Você pode interromper (Ctrl+C) e retomar depois!")
    print("💾 Cada resultado é salvo automaticamente no mesmo arquivo CSV")
    
    try:
        analyzer.run_analysis(num_repos=10, max_workers=3)
    except KeyboardInterrupt:
        print("\n🛑 Análise interrompida pelo usuário")
        print("💾 Resultados já salvos no arquivo CSV")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if analyzer.results:
            print("\n" + "="*50)
            analyzer.print_summary()

if __name__ == "__main__":
    main()
