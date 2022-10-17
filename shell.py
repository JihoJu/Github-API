import time
import requests
import click
from collections import OrderedDict
from github import Github
import json
import sys
import csv
import random


def write_commit_info_in_json(data, path):
    """ Json 파일로 저장

    :param data: 모든 public repo 의 정보
    :return:
    """

    with open(f'./{path}', 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=5)


def read_file(path):
    """ 파일 내 Github ID 를 읽기 위한 함수

    :param path: 파일 경로
    :return: github id generator
    """
    with open(f'{path}', 'r') as f:
        contents = f.readlines()
        for github_id in contents:
            yield github_id.strip().split()[1]


class GitHubAPIShell:
    """ GitHub API 객체

    - pygithub 라이브러리 사용
    - token 이 필요!! : 만약 token 과 함께 Github 객체 호출 시 id or IP 당 1시간에 60번 밖에 호출을 못함
    """

    def __init__(self, argv):
        self.g = Github(login_or_token="<token>")  # github api object
        self.header = {'Accept': 'application/vnd.github.v3+json',
                       'Authorization': 'Bearer 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'}
        self.filepath = argv  # argv: Github ID를 담은 파일 경로
        self.user = None  # GitHub user 객체 담기 위함
        self.languages_url = list()
        self.repo_objs = list()  # repo 객체 담기 위함 -> Commit data 를 가져오기 위함

    def run(self):
        start_time = time.time()
        gen = read_file(self.filepath)  # 파일 데이터 generator
        # self.write_user_info_in_csv(gen)  # 유저 정보 csv 파일에 저장
        self.write_repository_info_in_csv(gen)
        # self.write_language_info_in_csv()
        self.write_commit_info_in_csv()
        end_time = time.time()
        print(round(end_time - start_time, 3))

        return 0

    def write_user_info_in_csv(self, gen):
        with open('./member.csv', 'w') as f:
            wr = csv.writer(f)
            wr.writerow(["Github_id", "Avatar_url", "User_name", "Company", "Bio", "Location", "User_github_url", \
                         "Ghchart_url", "Followers", "Level", "Group_cnt", "User_rank_id", "Super_github_id"])
            for github_id in gen:
                self.user = self.g.get_user(github_id)
                wr.writerow([value for _, value in self.get_user_info().items()])

    def write_repository_info_in_csv(self, gen):
        with open('./repository2.csv', 'w') as f:
            wr = csv.writer(f)
            wr.writerow(
                ["Repository_id", "Repo_name", "Repo_url", "Fork_count", "Stargazers_count", "Created_at", "Updated_at",
                 "Github_id", "Repo_rank_id", "Issue_count", "Pr_count", "Commit_count"])

            repo_id = 1  # 순차적으로 repo id를 주기 위함
            for github_id in gen:
                self.user = self.g.get_user(github_id)
                for _, values in self.get_repo_info().items():
                    wr.writerow([repo_id] + [value for _, value in values.items()])
                    repo_id += 1
                print(github_id)
            print("-----")

    def write_language_info_in_csv(self):
        with open('./language2.csv', 'w') as f:
            wr = csv.writer(f)
            wr.writerow(["Language", "Repo_id", "Language_byte"])

            for repo_name, lang_url in self.languages_url:
                for lang, byte in self.get_language_info(lang_url).items():
                    wr.writerow([lang, repo_name, byte])

    def write_commit_info_in_csv(self):
        with open('./commit.csv', 'w') as f:
            wr = csv.writer(f)
            wr.writerow(["Commit_id", "Commit_msg", "Author", "Date", "Commit_url", "Repository_id"])

            commit_id = 1  # 순차적으로 commit id를 주기 위함
            for github_id, username, repo in self.repo_objs:
                for commit_info in self.get_commits(github_id, username, repo):
                    wr.writerow([commit_id] + [val for _, val in commit_info.items()])
                    commit_id += 1

    def get_user_info(self):

        user_infos = OrderedDict()

        user_infos["login"] = self.user.login
        user_infos["avatar_url"] = self.user.avatar_url
        user_infos["name"] = self.user.name
        # user_infos["email"] = self.user.email
        user_infos["company"] = self.user.company
        user_infos["bio"] = self.user.bio
        user_infos["location"] = self.user.location
        user_infos["html_url"] = self.user.html_url
        user_infos["ghchart_url"] = f"https://ghchart.rshah.org/{self.user.login}"
        user_infos["followers"] = self.user.followers
        user_infos["level"] = 1
        user_infos["group_cnt"] = 0
        user_infos["user_rank_id"] = 0
        user_infos["super_github_id"] = random.randint(1, 50)
        # user_infos["languages"] = self.get_language_stat()

        return user_infos

    def get_repo_info(self):
        """
        - 레포 이름
        - 유저 url
        - 레포 스타 개수
        - 레포 생성 날짜
        - 레포 업데이트 날짜
        - 레포 사용 언어

        :return: repo_infos: 입력 깃헙 ID 의 public repo 의 정보를 dict 자료 형태로 리턴
        """
        repo_infos = OrderedDict()
        repos = self.user.get_repos()

        for repo in repos:
            self.languages_url.append((repo.name, repo.languages_url))
            self.repo_objs.append((self.user.login, self.user.name, repo))

            repo_infos[repo.full_name] = {
                "Repo_name": repo.name,
                "Repo_url": repo.svn_url,
                "Fork_count": repo.forks,
                "Stargazers_count": repo.stargazers_count,
                "Created_at": repo.created_at,
                "Updated_at": repo.updated_at,
                "Github_id": self.user.login,
                "Repo_rank_id": 1,
                "Issue_count": len(requests.get(repo.issues_url.replace("{/number}", "") + "?state=all",
                                                headers=self.header).json()),
                "Pr_count": len(requests.get(repo.pulls_url.replace("{/number}", "") + "?state=all",
                                             headers=self.header).json()),
                "Commit_count": 1
                # "updatedAt": "{0}-{1}-{2} {3}".format(updated.year, updated.month, updated.day,
                #                                       updated.time()),
                # "language_url": repo.languages_url,
                # "commitInfo": self.get_commits(repo)
            }

        return repo_infos

    @staticmethod
    def get_commits(githubid, username, repo):
        """
        커밋 메시지
        커밋터
        author
        커밋 날짜, 시간

        :param repo: Repository Object
        :return: param 으로 전달 받은 repo 의 모든 commit 각 정보를 list 자료 형태로 리턴
        """
        return_data = list()

        try:
            for commit in repo.get_commits():
                if commit.commit.committer.name == "GitHub" or \
                        (commit.commit.author.name.lower() != githubid.lower()
                         and commit.commit.author.name.lower() != username.lower()
                         and commit.commit.committer.name.lower() != githubid.lower()
                         and commit.commit.committer.name.lower() != username.lower()):
                    continue

                commit_message = " ".join(commit.commit.message.split())
                data = {
                    "Commit_msg": commit_message,
                    "Author": commit.commit.author.name,
                    "Date": commit.commit.author.date,
                    "Commit_url": commit.commit.html_url,
                    "Repository_id": repo.full_name,
                    # "date": "{0}-{1}-{2} {3}".format(commit_date.year, commit_date.month, commit_date.day,
                    #                                  commit_date.time())
                }
                return_data.append(data)
        except github.GithubException as e:
            print(repo.full_name, e)

        return return_data

    def get_language_info(self, url):
        """ 각 레포 마다 사용된 언어 정보

        :return: 입력 깃헙 ID 의 public repo 에 사용된 언어 정보를 dict 자료 형태로 리턴
        """

        res = requests.get(url, headers=self.header)

        return res.json()


def get_language_stat(self):
    """ 사용자 언어 통계량 계산

    :return: 깃헙 유저의 사용 언어별 퍼센트
    """
    langs = dict()
    lang_sum = 0
    for url in self.languages_url:
        repo_langs = requests.get(url, headers=self.header).json()
        for lang in repo_langs.keys():
            if lang in langs:
                langs[lang] += int(repo_langs[lang])
            else:
                langs[lang] = int(repo_langs[lang])
            lang_sum += int(repo_langs[lang])

    for lang in langs.keys():
        langs[lang] = round((langs[lang] / lang_sum) * 100, 3)

    sorted_dict = sorted(langs.items(), key=lambda item: item[1], reverse=True)

    return sorted_dict


@click.command()
# @click.option("--id", '-i', help="Enter the GitHub ID in str format", required=False)  # github id
@click.option("--path", '-p', help="Enter the file path containing githubIDs", required=False)  # file path
def main(path=None):
    if path is None:
        return 0

    return GitHubAPIShell(path).run()


if __name__ == '__main__':
    sys.exit(main())
