# Dockerfile (ENTRYPOINT를 사용한 최종 버전)

# 1. 베이스 이미지 설정
FROM python:3.11-slim

# 2. 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 복사
COPY . .

# 6. 포트 노출
EXPOSE 8080

# 7. ⭐ 컨테이너 시작 명령어 (가장 중요)
# functions-framework를 직접 실행하도록 설정합니다.
# CMD 대신 ENTRYPOINT를 사용하여 외부 설정의 영향을 받지 않도록 합니다.
ENTRYPOINT ["functions-framework", "--target=process_region_job", "--source=main.py", "--port=8080"]