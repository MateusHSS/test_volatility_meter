from pydriller import Repository, ModificationType

test_files_modifications = {}

def get_repository(path):
    return Repository(path, order='chronological', only_no_merge=True, only_modifications_with_file_types=['.py'])

def process_repo(url):
    repo = get_repository(url)

    process_commits(repo)

def is_file_mapped(path):
    return test_files_modifications.get(path, None) is not None

def process_commits(repo):
    print(f'Processing {sum(1 for _ in repo.traverse_commits())} commits')
    for commit in repo.traverse_commits():
        for file in commit.modified_files:

            new_path = file.new_path

            if not is_test_file(file.filename):
                continue

            if file.change_type == ModificationType.ADD:
                if is_file_mapped(new_path):
                    test_files_modifications[new_path] += 1
                else:
                    test_files_modifications[new_path] = 1

def is_test_file(file):
    if not file or not file.endswith('.py'):
        return False

    if file.endswith('_test.py'):
        return True

    if file.startswith('test_') and file.endswith('.py'):
        return True

    return False

def main():

    with open('repos.txt', 'r') as file:
        for repo_url in file:
            process_repo(repo_url)

    print(test_files_modifications)


if __name__ == '__main__':
    main()