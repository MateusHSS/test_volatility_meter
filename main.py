import csv
import sys
import os

from pydriller import Repository, ModificationType

clone_dir = './temp_repos'

all_repo_results = []

def get_repository(path):
    print('Getting repository from ' + path)

    if not os.path.exists(clone_dir):
        os.makedirs(clone_dir)

    return Repository(path.strip(), order='chronological', only_no_merge=True, only_modifications_with_file_types=['.py'], clone_repo_to=clone_dir)

def process_repo(url, language):
    print('Processing ' + url)
    repo = get_repository(url)

    return {'repo': url, 'modifications': process_commits(repo, language)}

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

def write_to_csv(results):
    print('Writing to csv')
    fieldnames = ['repo_url', 'file', 'modifications']
    if not results:
        return

    with open('result.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for result in results:
            repo_url = result['repo']
            modifications = result['modifications']

            for filepath, modifications_num in modifications.items():
                writer.writerow({'repo_url': repo_url, 'file': filepath, 'modifications': modifications_num})

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
        with open(file_path, 'r') as file:
            for repo_url in file:
                try:
                    result = process_repo(repo_url, language)

                    if result:
                        all_repo_results.append(result)
                except Exception as e:
                    print(f"!!! Falha ao processar {repo_url}: {e}")

        write_to_csv(all_repo_results)
    except FileNotFoundError:
        print(f"Erro: Arquivo {file_path} não encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)





if __name__ == '__main__':
    main()