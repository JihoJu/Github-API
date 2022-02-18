# GitHub Api for project

#### GitHub API 로 어떤 정보를 가져올 수 있는지 테스트 하기 위한 코드

# Testing 방법

git clone 후 Github-API 폴더 안에서 다음 명령어 수행

```
# setup 설치
pip install --editable . 
pip install -e .

# githubshell 실행 cli
github --id=<깃헙 이이디>
github -i <깃헙 이이디>

# 예시
github --id="jiahho"
github -i "jiahho"
```

- 가상환경 : anaconda (다른 가상환경이라도 상관 X)
- python version : 3.8.11

# 설명

입력한 깃헙 id 의 public repository 의 데이터를 json 파일에 저장

#### repo info

- 레포 이름
- 유저 이름
- 최근 업데이트 날짜
- 모든 commit 정보

#### commit info

- 커밋 메시지
- 커밋터
- author
- 커밋 날짜, 시간

### 주의

* github token 없이 GitHub 객체 호출 수 id, IP 당 1시간에 60번 호출만
  가능 [(Limit Rate)](https://docs.github.com/en/developers/apps/building-github-apps/rate-limits-for-github-apps)
* token 생성 후 shell.py:37 주석에 login_or_token 변수에 생성한 token 넣고 위의 setup 설치부터 다시 수행
    * [token 생성 link](https://leveloper.tistory.com/211)
