import sys
from warnings import catch_warnings

from pydriller import Repository, ModificationType

all_repo_results = []

def get_repository(path):
    return Repository(path, order='chronological', only_no_merge=True, only_modifications_with_file_types=['.py'])

def process_repo(url):
    repo = get_repository(url)

    return {'repo': url, 'modifications': process_commits(repo)}

def process_commits(repo):
    modifications = {}
    for commit in repo.traverse_commits():
        for file in commit.modified_files:

            old_path = file.old_path
            new_path = file.new_path

            if not is_test_file(file.filename):
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

def is_test_file(file):
    if not file or not file.endswith('.py'):
        return False

    if file.endswith('_test.py'):
        return True

    if file.startswith('test_') and file.endswith('.py'):
        return True

    return False

def main():
    if len(sys.argv) < 2:
        print('Uso: python main.py <caminho_para_o_arquivo_de_repositorios>')
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r') as file:
            for repo_url in file:
                try:
                    result = process_repo(repo_url)

                    if result:
                        all_repo_results.append(result)
                except Exception as e:
                    print(f"!!! Falha ao processar {repo_url}: {e}")

        print(sorted(all_repo_results, key=lambda repo: repo['modifications'], reverse=True))
    except FileNotFoundError:
        print(f"Erro: Arquivo {file_path} não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)





if __name__ == '__main__':
    main()