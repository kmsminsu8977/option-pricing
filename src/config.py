"""프로젝트 경로 설정 모듈.

모든 스크립트가 같은 입력/출력 폴더를 참조하도록 저장소 루트 기준 경로를 한곳에서 정의한다.
경로 상수만 모아두면 노트북, CLI 스크립트, 테스트 코드가 동일한 디렉터리 규칙을 공유할 수 있다.
"""

from pathlib import Path


# `src/config.py` 기준으로 두 단계가 아니라 부모 한 단계가 저장소 루트다.
BASE_DIR = Path(__file__).resolve().parent.parent

# 데이터 영역은 raw, processed, sample로 나누어 원천/가공/데모 데이터를 분리한다.
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"

# 산출물 영역은 차트, 테이블, 이미지로 나누어 보고서 작성 시 필요한 결과물을 찾기 쉽게 한다.
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
TABLES_DIR = OUTPUTS_DIR / "tables"
IMAGES_DIR = OUTPUTS_DIR / "images"

# 문서/노트북/참고자료/발표자료/아카이브는 코드와 분리해 프로젝트 산출물의 역할을 명확히 한다.
DOCS_DIR = BASE_DIR / "docs"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
REFERENCES_DIR = BASE_DIR / "references"
PRESENTATION_DIR = BASE_DIR / "presentation"
ARCHIVE_DIR = BASE_DIR / "archive"
