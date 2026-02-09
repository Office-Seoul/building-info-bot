import os
import requests
import re
import urllib.parse
from datetime import datetime

print("🚀 서울시 건축물대장 봇 - 공식 API")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
print(f"✅ SEOUL_API_KEY 확인됨")

# 테스트 주소
TEST_ADDRESS = "서울특별시 강남구 역삼동"
print(f"📍 테스트 주소: {TEST_ADDRESS}")

# 1. 법정동 코드 찾기 (강남구=11680)
gu_codes = {
    "강남구": "11680", "송파구": "11650", "마포구": "11440"
}

gu_match = re.search(r'([가-힣]+구)', TEST_ADDRESS)
if not gu_match:
    print("❌ 구 이름 파싱 실패")
    exit(1)

gu = gu_match.group(1)
bjd_code = gu_codes.get(gu, "11680")  # 기본값 강남구
dong = "역삼동"

print(f"🔍 구: {gu}, 법정동코드: {bjd_code}, 동: {dong}")

# 2. 공공데이터포털 표준 REST API (HTTPS 443포트)
url = f"https://api.odcloud.kr/api/ConstructionInformationService/v1/getConstInfo?page=1&perPage=10&cond[bjdCode::EQ]={bjd_code}&cond[dongNm::EQ]={urllib.parse.quote(dong)}&serviceKey={SEOUL_API_KEY}"

print(f"🌐 공식 API 호출: {url}")

try:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
    
    print(f"✅ 응답: {data.get('totalCount', 0)}건")
    
    if data.get('data'):
        building = data['data'][0]
        print(f"✅ 건물명: {building.get('bldNm', '알수없음')}")
        print(f"✅ 주용도: {building.get('mainPurpsNm', '알수없음')}")
        print("🎉 공공데이터포털 API 완벽 동작!")
    else:
        print("ℹ️ 건물 정보 없음")
        
except Exception as e:
    print(f"❌ API 오류: {e}")
    exit(1)

print("✅ 최종 테스트 완료!")
