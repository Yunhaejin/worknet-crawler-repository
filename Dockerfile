# Dockerfile (최종 수정본)

# 1. 베이스 이미지 설정 (Python 3.11 버전 사용)
FROM python:3.11-slim

# 2. 시스템 패키지 업데이트 및 Chrome/Chromedriver와 의존성 라이브러리 설치
# --no-install-recommends 로 불필요한 패키지 설치를 막아 이미지 크기를 최적화합니다.
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. requirements.txt 파일을 컨테이너에 복사
COPY requirements.txt .

# 5. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 6. 현재 폴더의 모든 파일을 컨테이너의 작업 디렉토리로 복사
COPY . .

# 7. 포트 노출
EXPOSE 8080

# 8. 컨테이너 시작 명령어
CMD ["functions-framework", "--target=batch_crawl_trigger", "--source=main.py", "--port=8080"]
