# Dockerfile

# 1. 베이스 이미지 설정 (Python 3.11 버전 사용)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. requirements.txt 파일을 컨테이너에 복사
COPY requirements.txt .

# 4. requirements.txt에 명시된 라이브러리 설치
# --no-cache-dir 옵션은 불필요한 캐시를 남기지 않아 이미지 크기를 줄여줍니다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. 현재 폴더의 모든 파일을 컨테이너의 작업 디렉토리로 복사
COPY . .

# 6. 구글 클라우드에서 사용하는 기본 포트 8080을 외부에 노출
EXPOSE 8080

# 7. 컨테이너가 시작될 때 실행할 명령어 설정
# functions-framework를 사용하여 main.py 파일의 batch_crawl_trigger 함수를 실행
CMD ["functions-framework", "--target=batch_crawl_trigger", "--source=main.py", "--port=8080"]