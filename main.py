import csv
import sys
import os
import shutil
import gc
import stat
from multiprocessing import Pool, cpu_count

from pydriller import Repository, ModificationType

clone_dir = './temp_repos'

all_repo_results = []

def get_repository(path, language) -> Repository:
    print('Getting repository from ' + path)

    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)

    file_type = ''
    if language == 'py':
        file_type = '.py'
    elif language == 'ts':
        file_type = '.ts'
    elif language == 'js':
        file_type = '.js'

    return Repository(path.strip(), order='chronological', only_no_merge=True, only_modifications_with_file_types=[file_type], clone_repo_to=clone_dir)

def get_repo_name_from_url(url) -> str:
    last_slash_index = url.rfind('/')
    len_url = len(url)

    if last_slash_index < 0 or last_slash_index >= len_url - 1:
        print('URL mal formada')
        sys.exit(1)

    last_dot_index = url.rfind(".")

    if url[last_dot_index:] == ".git":
        last_suffix_index = last_dot_index
    else:
        last_suffix_index = len_url

    return url[last_slash_index + 1:last_suffix_index]

def remove_readonly(func, path, exc_info):
    if isinstance(exc_info[1], PermissionError):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            raise exc_info[1]
    else:
        raise exc_info[1]

def process_repo(url, language):
    print('Processing ' + url)
    repo = None
    try:
        repo = get_repository(url, language)
        repo_name = get_repo_name_from_url(url)

        write_to_csv(repo_name, process_commits(repo, language))
    except Exception as e:
        print(f"!!!Falha ao processar {url}: {e}")
        return None
    finally:
        print("Iniciando limpeza...")
        if repo is not None:
            del repo
            gc.collect()

        repo_temp_path = os.path.join(clone_dir, get_repo_name_from_url(url))
        if os.path.exists(repo_temp_path):
            shutil.rmtree(repo_temp_path, onerror=remove_readonly)

            print(f"Diretório {repo_temp_path} deletado com sucesso.")
        else:
            print(f"Diretório {repo_temp_path} não encontrado, nada a limpar.")


def process_commits(repo, language):
    print('Processing commits')
    modifications = {}
    for commit in repo.traverse_commits():
        for file in commit.modified_files:
            old_path = file.old_path
            new_path = file.new_path

            if not is_test_file(file.filename, language):
                continue

            if file.change_type == ModificationType.ADD:
                if new_path in modifications:
                    modifications[new_path] += 1
                else:
                    modifications[new_path] = 1
            elif file.change_type == ModificationType.RENAME:
                if old_path in modifications:
                    modifications[new_path] = modifications[old_path] + 1
                else:
                    modifications[new_path] = modifications[old_path] = 1
            elif file.change_type == ModificationType.DELETE:
                if old_path in modifications:
                    modifications[old_path] += 1
            elif file.change_type == ModificationType.MODIFY:
                if new_path in modifications:
                    modifications[new_path] += 1
                else:
                    modifications[new_path] = 1

    return modifications

def is_py_test_file(file):
    if not file or not file.endswith('.py'):
        return False

    if file.endswith('_test.py'):
        return True

    if file.startswith('test_') and file.endswith('.py'):
        return True

    return False

def is_js_test_file(file):
    if not file or not file.endswith('.js'):
        return False

    if file.endswith('.test.js') or file.endswith('.spec.js'):
        return True

    return False

def is_ts_test_file(file):
    if not file or not file.endswith('.ts'):
        return False

    if file.endswith('.test.ts') or file.endswith('.spec.ts'):
        return True

    return False

def is_test_file(file, language):
    if language == 'py':
        return is_py_test_file(file)
    elif language == 'ts':
        return is_ts_test_file(file)
    elif language == 'js':
        return is_js_test_file(file)
    else:
        return False

def write_to_csv(repo_name, result, output_dir='results'):
    fieldnames = ['file', 'modifications']
    if not result:
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    result_filename = f'{repo_name}.csv'
    result_file_path = os.path.join(output_dir, result_filename)

    with open(result_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for filepath, modifications_num in result.items():
            writer.writerow({'file': filepath, 'modifications': modifications_num})

    return

def main():
    if len(sys.argv) < 3:
        print('Uso: python main.py <linguagem> <caminho_para_o_arquivo_de_repositorios>')
        sys.exit(1)

    language = sys.argv[1]
    file_path = sys.argv[2]

    if language not in ['py', 'ts', 'js']:
        print('As linguagens suportadas atualmente são: "py", "ts", "js"')
        sys.exit(1)

    try:
        repo_tasks = []
        with open(file_path, 'r') as file:
            for repo_url in file:
                repo_tasks.append((repo_url.strip(), language))

        num_workers = max(1, cpu_count() - 1)
        print(f"Iniciando Pool de Processos com {num_workers} workers")

        with Pool(num_workers) as p:
            p.starmap(process_repo, repo_tasks)

    except FileNotFoundError:
        print(f"Erro: Arquivo {file_path} não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)





if __name__ == '__main__':
    main()