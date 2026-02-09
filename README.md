# Web Content Integrity Monitor

웹 페이지를 마크다운으로 아카이브하고, **일별 스냅샷 비교**로 콘텐츠 변경을 감지하는 도구입니다.  
URL 목록(CSV)을 입력받아 HTML을 정제·변환한 뒤 날짜별로 압축 저장하고, N일 전과 오늘 아카이브를 비교해 변경된 페이지 목록을 출력합니다.

---

## 주요 기능

| 구성요소 | 설명 |
|----------|------|
| **html2md** | CSV의 URL에서 HTML을 받아 본문만 추출한 뒤 마크다운(.md)으로 변환하고, 당일 타임스탬프로 tar.gz 아카이브 생성 |
| **diffcheck** | 오늘 아카이브와 N일 전 아카이브를 풀어 본문만 정규화한 뒤 비교 → 변경된 페이지의 제목·URL 출력 |

---

## 요구사항

- **Python 3.10+**
- 의존성: `beautifulsoup4`, `requests`  
  (테스트 실행 시 `pytest`)

**설치 (Conda):**

```bash
conda env create -f environment.yml
conda activate html-converter
```

**설치 (pip):**

```bash
pip install -r requirements.txt
```

---

## 사용법

### 1. 입력 CSV 형식

파이프(`|`)로 구분된 3열:

```
제목|URL|날짜(YYYY-MM-DD)
```

예:

```
Python (programming language)|https://en.wikipedia.org/wiki/Python_(programming_language)|2025-02-09
Web scraping|https://en.wikipedia.org/wiki/Web_scraping|2025-02-09
```

- `날짜`가 오늘보다 미래인 행은 건너뜁니다.

### 2. 웹 페이지 수집 및 아카이브 (html2md)

```bash
./html2md <csv_file> <output_dir>
```

- `output_dir`에 `YYYY-MM-DD_HH-MM-SS.tar.gz` 형태로 아카이브가 생성됩니다.
- 내부는 변환된 `.md` 파일들 (파일명은 제목 기반으로 자동 생성).

**예시:**

```bash
./html2md sample_input.csv ./output
# Converted: Python (programming language) -> python_programming_language.md
# Archive created: ./output/2025-02-09_14-30-00.tar.gz
```

### 3. N일 간 변경 페이지 확인 (diffcheck)

```bash
./diffcheck <N> <output_dir>
```

- `output_dir`에서 **오늘**과 **N일 전** 날짜의 아카이브를 찾아 비교합니다.
- 같은 파일명(같은 페이지)만 비교하며, 본문이 바뀐 페이지만 출력합니다.

**예시:**

```bash
./diffcheck 7 ./output
# The following web pages have been modified in the last 7 days:
# - Python (programming language) (https://en.wikipedia.org/wiki/...)
```

---

## Quick Start

```bash
# 의존성 설치
pip install -r requirements.txt

# 샘플로 수집 (실제 위키 URL 사용 시 네트워크 필요)
./html2md sample_input.csv ./output

# 7일 전 vs 오늘 비교 (해당 날짜 아카이브가 있어야 함)
./diffcheck 7 ./output
```

**Makefile 사용:**

```bash
make crawl      # html2md sample_input.csv output
make diff N=7   # diffcheck 7 output
```

---

## Cron으로 정기 수집

매일 같은 시간에 `html2md`를 실행하면 일별 스냅샷이 쌓이고, `diffcheck`로 “지난 N일 동안 바뀐 페이지”를 확인할 수 있습니다.

예시 (`cronjob.txt` 참고):

```cron
30 03 * * * /usr/bin/python3 /path/to/html2md /path/to/input.csv /path/to/output_dir >> /path/to/downloads.log 2>&1
```

---

## 프로젝트 구조

```
.
├── html2md           # 크롤링 + HTML→MD 변환 + 아카이브
├── diffcheck         # N일 전/오늘 아카이브 비교
├── environment.yml   # Conda 환경
├── requirements.txt  # pip 의존성
├── sample_input.csv  # 샘플 URL 목록
├── cronjob.txt       # Cron 예시
├── Makefile          # crawl / diff 타깃
├── docs/
│   └── DESIGN.md     # 설계·기술 노트
└── tests/
    ├── fixtures/           # minimal_mw.html for local tests
    ├── test_diffcheck.py
    └── test_html2md.py
```

---

## 테스트

```bash
pytest tests/ -v
```

---

## 라이선스 / 목적

교육·포트폴리오 목적입니다. 실제 웹사이트 수집 시 해당 사이트의 이용 약관과 robots.txt를 확인하세요.
