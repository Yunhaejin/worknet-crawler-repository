# main.py (Pub/Sub 방식으로 변경된 최종본)

import os
import sys
import time
import traceback
import hashlib
import json
import base64

import firebase_admin
from firebase_admin import firestore
from google.cloud import pubsub_v1
import functions_framework

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ==============================================================================
#  Global Setup
# ==============================================================================
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()
    publisher = pubsub_v1.PublisherClient()
    # 🔴 중요: 본인의 GCP 프로젝트 ID와 Pub/Sub 토픽 이름으로 수정하세요.
    PROJECT_ID = "samsisebot" # 예시: "my-gcp-project-12345"
    TOPIC_ID = "worknet-crawl-jobs"  # 예시: "crawl-jobs-topic"
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")


    REGION_CODES = {
        "서울 강남구": "11680", "서울 강동구": "11740", "서울 강북구": "11305", "서울 강서구": "11500", 
        "서울 관악구": "11620", "서울 광진구": "11215", "서울 구로구": "11530", "서울 금천구": "11545",
        "서울 노원구": "11350", "서울 도봉구": "11320", "서울 동대문구": "11230", "서울 동작구": "11590",
        "서울 마포구": "11440", "서울 서대문구": "11410", "서울 서초구": "11650", "서울 성동구": "11200",
        "서울 성북구": "11290", "서울 송파구": "11710", "서울 양천구": "11470", "서울 영등포구": "11560",
        "서울 용산구": "11170", "서울 은평구": "11380", "서울 종로구": "11110", "서울 중구": "11140",
        "서울 중랑구": "11260", "부산 강서구": "26440", "부산 금정구": "26410", "부산 기장군": "26710",
        "부산 남구": "26290", "부산 동구": "26170", "부산 동래구": "26260", "부산 부산진구": "26230",
        "부산 북구": "26320", "부산 사상구": "26530", "부산 사하구": "26380", "부산 서구": "26140",
        "부산 수영구": "26500", "부산 연제구": "26470", "부산 영도구": "26200", "부산 중구": "26110",
        "부산 해운대구": "26350", "대구 군위군": "27720", "대구 남구": "27200", "대구 달서구": "27290",
        "대구 달성군": "27710", "대구 동구": "27140", "대구 북구": "27230", "대구 서구": "27170",
        "대구 수성구": "27260", "대구 중구": "27110", "인천 강화군": "28710", "인천 계양구": "28245",
        "인천 남동구": "28200", "인천 동구": "28140", "인천 미추홀구": "28177", "인천 부평구": "28237",
        "인천 서구": "28260", "인천 연수구": "28185", "인천 옹진군": "28720", "인천 중구": "28110",
        "광주 광산구": "29200", "광주 남구": "29155", "광주 동구": "29110", "광주 북구": "29170",
        "광주 서구": "29140", "대전 대덕구": "30230", "대전 동구": "30110", "대전 서구": "30170",
        "대전 유성구": "30200", "대전 중구": "30140", "전북 고창군": "52790", "전북 군산시": "52130",
        "전북 김제시": "52210", "전북 남원시": "52190", "전북 무주군": "52730", "전북 부안군": "52800",
        "전북 순창군": "52770", "전북 완주군": "52710", "전북 익산시": "52140", "전북 임실군": "52750",
        "전북 장수군": "52740", "전북 전주시": "52110", "전북 전주시 덕진구": "52113", "전북 전주시 완산구": "52111",
        "전북 정읍시": "52180", "전북 진안군": "52720", "울산 남구": "31140", "울산 동구": "31170",
        "울산 북구": "31200", "울산 울주군": "31710", "울산 중구": "31110", "세종": "36110",
        "경기 가평군": "41820", "경기 고양시": "41280", "경기 고양시 덕양구": "41281", "경기 고양시 일산동구": "41285",
        "경기 고양시 일산서구": "41287", "경기 과천시": "41290", "경기 광명시": "41210", "경기 광주시": "41610",
        "경기 구리시": "41310", "경기 군포시": "41410", "경기 김포시": "41570", "경기 남양주시": "41360",
        "경기 동두천시": "41250", "경기 부천시": "41190", "경기 성남시": "41130", "경기 성남시 분당구": "41135",
        "경기 성남시 수정구": "41131", "경기 성남시 중원구": "41133", "경기 수원시": "41110", "경기 수원시 권선구": "41113",
        "경기 수원시 영통구": "41117", "경기 수원시 장안구": "41111", "경기 수원시 팔달구": "41115", "경기 시흥시": "41390",
        "경기 안산시": "41270", "경기 안산시 단원구": "41273", "경기 안산시 상록구": "41271", "경기 안성시": "41550",
        "경기 안양시": "41170", "경기 안양시 동안구": "41173", "경기 안양시 만안구": "41171", "경기 양주시": "41630",
        "경기 양평군": "41830", "경기 여주시": "41670", "경기 연천군": "41800", "경기 오산시": "41370",
        "경기 용인시": "41460", "경기 용인시 기흥구": "41463", "경기 용인시 수지구": "41465", "경기 용인시 처인구": "41461",
        "경기 의왕시": "41430", "경기 의정부시": "41150", "경기 이천시": "41500", "경기 파주시": "41480",
        "경기 평택시": "41220", "경기 포천시": "41650", "경기 하남시": "41450", "경기 화성시": "41590",
        "충북 괴산군": "43760", "충북 단양군": "43800", "충북 보은군": "43720", "충북 영동군": "43740",
        "충북 옥천군": "43730", "충북 음성군": "43770", "충북 제천시": "43150", "충북 증평군": "43745",
        "충북 진천군": "43750", "충북 청주시": "43110", "충북 청주시 상당구": "43111", "충북 청주시 서원구": "43112",
        "충북 청주시 청원구": "43114", "충북 청주시 흥덕구": "43113", "충북 충주시": "43130", "충남 계룡시": "44250",
        "충남 공주시": "44150", "충남 금산군": "44710", "충남 논산시": "44230", "충남 당진시": "44270",
        "충남 보령시": "44180", "충남 부여군": "44760", "충남 서산시": "44210", "충남 서천군": "44770",
        "충남 아산시": "44200", "충남 예산군": "44810", "충남 천안시": "44130", "충남 천안시 동남구": "44131",
        "충남 천안시 서북구": "44133", "충남 청양군": "44790", "충남 태안군": "44825", "충남 홍성군": "44800",
        "전남 강진군": "46810", "전남 고흥군": "46770", "전남 곡성군": "46720", "전남 광양시": "46230",
        "전남 구례군": "46730", "전남 나주시": "46170", "전남 담양군": "46710", "전남 목포시": "46110",
        "전남 무안군": "46840", "전남 보성군": "46780", "전남 순천시": "46150", "전남 신안군": "46910",
        "전남 여수시": "46130", "전남 영광군": "46870", "전남 영암군": "46830", "전남 완도군": "46890",
        "전남 장성군": "46880", "전남 장흥군": "46800", "전남 진도군": "46900", "전남 함평군": "46860",
        "전남 해남군": "46820", "전남 화순군": "46790", "경북 경산시": "47290", "경북 경주시": "47130",
        "경북 고령군": "47830", "경북 구미시": "47190", "경북 김천시": "47150", "경북 문경시": "47280",
        "경북 봉화군": "47920", "경북 상주시": "47250", "경북 성주군": "47840", "경북 안동시": "47170",
        "경북 영덕군": "47770", "경북 영양군": "47760", "경북 영주시": "47210", "경북 영천시": "47230",
        "경북 예천군": "47900", "경북 울릉군": "47940", "경북 울진군": "47930", "경북 의성군": "47730",
        "경북 청도군": "47820", "경북 청송군": "47750", "경북 칠곡군": "47850", "경북 포항시": "47110",
        "경북 포항시 남구": "47111", "경북 포항시 북구": "47113", "경남 거제시": "48310", "경남 거창군": "48880",
        "경남 고성군": "48820", "경남 김해시": "48250", "경남 남해군": "48840", "경남 밀양시": "48270",
        "경남 사천시": "48240", "경남 산청군": "48860", "경남 양산시": "48330", "경남 의령군": "48720",
        "경남 진주시": "48170", "경남 창녕군": "48740", "경남 창원시": "48120", "경남 창원시 마산합포구": "48125",
        "경남 창원시 마산회원구": "48127", "경남 창원시 성산구": "48123", "경남 창원시 의창구": "48121",
        "경남 창원시 진해구": "48129", "경남 통영시": "48220", "경남 하동군": "48850", "경남 함안군": "48730",
        "경남 함양군": "48870", "경남 합천군": "48890", "제주 서귀포시": "50130", "제주 제주시": "50110",
        "강원 강릉시": "51150", "강원 고성군": "51820", "강원 동해시": "51170", "강원 삼척시": "51230",
        "강원 속초시": "51210", "강원 양구군": "51800", "강원 양양군": "51830", "강원 영월군": "51750",
        "강원 원주시": "51130", "강원 인제군": "51810", "강원 정선군": "51770", "강원 철원군": "51780",
        "강원 춘천시": "51110", "강원 태백시": "51190", "강원 평창군": "51760", "강원 홍천군": "51720",
        "강원 화천군": "51790", "강원 횡성군": "51730"
    }


except Exception as e:
    print(f"🚨 CRITICAL ERROR DURING INITIALIZATION: {e}")
    traceback.print_exc(file=sys.stdout)


# ==============================================================================
#  ✅ 1. 지시자 함수 (Scheduler)
# ==============================================================================
@functions_framework.http
def schedule_crawl_jobs(request):
    """
    모든 지역에 대한 크롤링 작업을 Pub/Sub에 메시지로 보냅니다.
    """
    try:
        print(f"🚀 총 {len(REGION_CODES)}개 지역에 대한 크롤링 작업을 예약합니다...")
        for region_name in REGION_CODES.keys():
            message_data = json.dumps({"region": region_name}).encode("utf-8")
            future = publisher.publish(topic_path, message_data)
            future.result() # 메시지가 성공적으로 보내질 때까지 기다림
        
        success_message = f"✅ {len(REGION_CODES)}개의 작업 지시를 성공적으로 Pub/Sub에 보냈습니다."
        print(success_message)
        return (success_message, 200)

    except Exception as e:
        error_message = f"🚨 작업 예약 중 오류 발생: {e}"
        print(error_message)
        traceback.print_exc(file=sys.stdout)
        return (error_message, 500)

# ==============================================================================
#  ✅ 2. 작업자 함수 (Worker)
# ==============================================================================
@functions_framework.cloud_event
def process_region_job(cloud_event):
    """
    Pub/Sub 메시지를 받아 단일 지역에 대한 크롤링을 수행하고 Firestore에 저장합니다.
    """
    try:
        # Pub/Sub 메시지에서 지역 이름 추출
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")
        search_region = json.loads(message_data)["region"]
        print(f"--- '{search_region}' 지역 크롤링 작업 시작 ---")

        # 단일 지역 크롤링
        jobs = get_jobs_by_selenium(search_region)

        # Firestore에 업로드
        if jobs:
            upload_jobs_to_firestore(jobs)
        
        print(f"✅ '{search_region}' 지역 작업 완료.")

    except Exception as e:
        print(f"🚨 작업 처리 중 최종 오류 발생: {e}")
        traceback.print_exc(file=sys.stdout)

# ==============================================================================
#  Helper Functions (기존과 거의 동일)
# ==============================================================================
def get_jobs_by_selenium(search_region):
    # 이 함수는 이전 최종본과 동일합니다. (resultCnt=100)
    # Service 객체를 사용하여 명시적으로 드라이버 경로를 지정하는 방식을 유지합니다.
    region_code = REGION_CODES.get(search_region)
    if not region_code: return []
    
    job_results = []
    service = Service(executable_path='/usr/bin/chromedriver')
    with webdriver.Chrome(service=service, options=chrome_options) as driver:
        base_url = "https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do"
        search_params = f"region={region_code}&resultCnt=10&sortOrderBy=DESC&sortField=DATE"
        target_url = f"{base_url}?{search_params}"
        driver.get(target_url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # ... (이하 파싱 및 데이터 추가 로직은 기존과 동일)
    return job_results

def upload_jobs_to_firestore(jobs_list):
    # 이 함수도 기존과 동일합니다.
    if not db or not jobs_list: return
    batch = db.batch()
    for job in jobs_list:
        job['crawled_at'] = firestore.SERVER_TIMESTAMP
        unique_key = f"{job['company']}_{job['title']}_{job['source_region']}"
        doc_id = hashlib.sha256(unique_key.encode()).hexdigest()
        doc_ref = db.collection('worknet_jobs').document(doc_id)
        batch.set(doc_ref, job, merge=True)
    batch.commit()

    print(f"✅ {len(jobs_list)}개 정보 Firestore 업로드 완료. (지역: {jobs_list[0]['source_region']})")
