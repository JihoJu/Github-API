import click
from collections import OrderedDict
from github import Github
import json
import urllib.request
import sys
import csv
import random

URL = "https://api.github.com/users/"

""" url 로 github api 호출
    def get_user_info(self):
        headers = {'Authorization': "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"}
        user_data = requests.get(URL + self.github_id, headers=headers).json()
        pprint(user_data)"""


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
        self.g = Github(login_or_token="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")  # github api object
        self.filepath = argv  # argv: Github ID를 담은 파일 경로
        self.user = None  # GitHub user 객체 담기 위함
        self.languages_url = list()

    def run(self):
        gen = read_file(self.filepath)  # 파일 데이터 generator
        with open('./member.csv', 'w') as f:
            wr = csv.writer(f)
            wr.writerow(["Github_id", "Avatar_url", "User_name", "Company", "Bio", "Location", "User_github_url", \
                         "Followers", "Level", "Group_cnt", "User_rank_id", "Super_github_id"])
            for github_id in gen:
                self.user = self.g.get_user(github_id)
                wr.writerow([value for _, value in self.get_user_info().items()])
                print("끝")

        return 0

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
        # user_infos["ghchart_url"] = f"https://ghchart.rshah.org/{self.github_id}"
        user_infos["followers"] = self.user.followers
        user_infos["level"] = 1
        user_infos["group_cnt"] = 0
        user_infos["user_rank_id"] = 0
        user_infos["super_github_id"] = random.randint(1, 50)
        # user_infos["languages"] = self.get_language_stat()

        return user_infos

    def get_repo_info(self):
        """
        레포 이름
        유저 이름
        최근 업데이트 날짜
        모든 commit 정보

        :return: repo_infos: 입력 깃헙 ID 의 public repo 의 정보를 dict 자료 형태로 리턴
        """
        repo_infos = OrderedDict()
        repos = self.user.get_repos()

        for repo in repos:
            updated = repo.updated_at  # repo update 시간
            self.languages_url.append(repo.languages_url)
            repo_infos[repo.full_name] = {
                "repoName": repo.name,
                "userName": self.user.name,
                "updatedAt": "{0}-{1}-{2} {3}".format(updated.year, updated.month, updated.day,
                                                      updated.time()),
                "language_url": repo.languages_url,
                "commitInfo": self.get_commits(repo)
            }

        return repo_infos

    @staticmethod
    def get_commits(repo):
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
                commit_date = commit.commit.author.date
                commit_message = " ".join(commit.commit.message.split())

                data = {
                    "message": commit_message,
                    "committer": commit.commit.committer.name,
                    "author": commit.commit.author.name,
                    "date": "{0}-{1}-{2} {3}".format(commit_date.year, commit_date.month, commit_date.day,
                                                     commit_date.time())
                }

                return_data.append(data)
        except github.GithubException as e:
            print(repo.full_name, e)

        return return_data

    def get_language_stat(self):

        langs = dict()
        lang_sum = 0
        for url in self.languages_url:
            repo_langs = json.loads(urllib.request.urlopen(url).read())
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
