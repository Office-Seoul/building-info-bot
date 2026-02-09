import os
import requests
from datetime import datetime

print("🚀 서울시 건축물대장 봇 시작!")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
print(f"✅ SEOUL_API_KEY 확인됨")

# 하드코딩 테스트 주소 (실제 Notion 주소 대신)
TEST_ADDRESS = "서울 강남구 역삼동"
print(f"📍 테스트 주소: {TEST_ADDRESS}")

# 동 이름 추출 (더 강력한 정규식)
import re
dong_match = re.search(r'([가-힣]+구[가-힣\s]*동)', TEST_ADDRESS)
if not dong_match:
    print("❌ 주소에서 동 파싱 실패")
    exit(1)

dong = dong_match.group(1).strip()
print(f"🔍 검색 동: {dong}")

# 서울시 API 호출
url = f"https://api.seoul.go.kr:8088/openapi/buildingInfo/json/{SEOUL_API_KEY}/1/5/11680/{dong}"
print(f"🌐 API 호출: {url}")

try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    buildings = data.get('buildingInfo', [])
    print(f"📊 건물 수: {len(buildings)}")
    
    if buildings:
        building = buildings[0]
        print(f"✅ 건물명: {building.get('bdNm', '알수없음')}")
        print(f"✅ 주용도: {building.get('mainPurpsNm', '알수없음')}")
        print(f"✅ 연면적: {building.get('totArea', '0')}㎡")
        print(f"✅ 층수: {building.get('totFlrCnt', '0')}층")
        print("🎉 서울시 API 완벽 동작!")
    else:
        print("ℹ️ 해당 동에 등록된 건물 없음")
        
except Exception as e:
    print(f"❌ API 오류: {e}")
    exit(1)

print("✅ 테스트 완료!")
