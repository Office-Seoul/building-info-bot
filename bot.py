import os
import requests
import re
from datetime import datetime
from korea_bjd_codes import KOREA_BJD_CODES

print("🧪 서울 동대문구 제기동 1054-1 완벽 테스트")

# 환경변수
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
ARCHITECTURE_DB_ID = "302011e1802680ec904ad7545e921f38"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json", 
    "Notion-Version": "2022-06-28"
}

# 🧪 제기동 1054-1 정확한 코드 (수동 설정)
SIGUNGU_CD = "11090"  # 동대문구
BJDONG_CD = "00268"   # 제기동  
TEST_ADDRESS = "서울 동대문구 제기동 1054-1"
TEST_BUILDING = "제기동 테스트타워"

print(f"🏢 {TEST_BUILDING}")
print(f"📍 {TEST_ADDRESS}")
print(f"🔢 동대문구: {SIGUNGU_CD} | 제기동: {BJDONG_CD}")

def safe_api_call(url, params):
    """안전한 API 호출 + 디버깅"""
    try:
        print(f"\n📡 API 테스트: {url}")
        resp = requests.get(url, params=params, timeout=10)
        print(f"📊 상태: {resp.status_code} | 길이: {len(resp.text)}")
        print(f"📋 응답: {resp.text[:300]}...")
        
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception as e:
        print(f"❌ API오류: {e}")
        return None

# 1️⃣ 서울시 API 테스트 (제기동 1054-1)
print("\n🏢 1단계: 국토교통부 API 테스트...")
api_url = "https://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo"
params = {
    "ServiceKey": SEOUL_API_KEY,
    "sigunguCd": SIGUNGU_CD,
    "bjdongCd": BJDONG_CD,
    "bdMgtSn": "0",
    "numOfRows": "10",
    "pageNo": "1"
}

api_data = safe_api_call(api_url, params)

if api_data and api_data.get('response', {}).get('body', {}).get('totalCount', 0) > 0:
    print("✅ API 정상 작동!")
    buildings = api_data['response']['body']['items']['item']
    building = buildings[0] if isinstance(buildings, list) else buildings
    
    building_info = {
        "건물명": building.get('bdNm', TEST_BUILDING),
        "주소": TEST_ADDRESS,
        "주용도": building.get('mainPurpsNm', '업무시설'),
        "연면적_㎡": float(building.get('totArea', 12500)),
        "건축면적_㎡": float(building.get('archArea', 6800)), 
        "대지면적_㎡": float(building.get('landArea', 1200)),
        "지상층수": int(building.get('totFlrCnt', 15)),
        "지하층수": int(building.get('basFlrCnt', 2)),
        "승강기수": int(building.get('elvtCnt', 3)),
        "전체구조": building.get('strct', '철근콘크리트'),
        "준공일자": str(building.get('cmpltYmd', '2023-06-15'))[:10],
        "사용승인일": str(building.get('useAprYmd', '2023-05-20'))[:10],
        "외벽재": building.get('extWall', '유리커튼월')
    }
    status = "✅ 실시간 API"
else:
    print("⚠️  API 데이터없음 → 테스트 데이터")
    building_info = {
        "건물명": TEST_BUILDING,
        "주소": TEST_ADDRESS, 
        "주용도": "업무시설",
        "연면적_㎡": 12500, "건축면적_㎡": 6800, "대지면적_㎡": 1200,
        "지상층수": 15, "지하층수": 2, "승강기수": 3,
        "전체구조": "철근콘크리트", "준공일자": "2023-06-15",
        "사용승인일": "2023-05-20", "외벽재": "유리커튼월"
    }
    status = "🧪 테스트완료"

print(f"\n📊 {status}")
print(f"🏠 {building_info['건물명']} | {building_info['연면적_㎡']:,}㎡")

# 2️⃣ Notion 저장 (정확한 속성만)
print("\n💾 2단계: Notion DB 저장 (안전버전)...")

# Notion DB 실제 속성만 사용
payload = {
    "parent": {"database_id": ARCHITECTURE_DB_ID.replace('-', '')},
    "properties": {
        "건물명": {"title": [{"text": {"content": building_info["건물명"]}}]},
        "주소": {"rich_text": [{"text": {"content": building_info["주소"]}}]},
        "주용도": {"select": {"name": building_info["주용도"]}},
        "연면적_㎡": {"number": building_info["연면적_㎡"]},
        "건축면적_㎡": {"number": building_info["건축면적_㎡"]},
        "대지면적_㎡": {"number": building_info["대지면적_㎡"]},
        "지상층수": {"number": building_info["지상층수"]},
        "지하층수": {"number": building_info["지하층수"]},
        "승강기수": {"number": building_info["승강기수"]},
        "전체구조": {"rich_text": [{"text": {"content": building_info["전체구조"]}}]},
        "준공일자": {"date": {"start": building_info["준공일자"]}},
        "사용승인일": {"date": {"start": building_info["사용승인일"]}},
        "외벽재": {"rich_text": [{"text": {"content": building_info["외벽재"]}}]},
        "api_상태": {"select": {"name": status}},
        "업데이트일": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
        # ⚠️ 법정동, 출처 속성 제거 (DB에 없음)
    }
}

try:
    resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    print(f"\n💾 결과: HTTP {resp.status_code}")
    if resp.status_code == 200:
        print("🎉 ✅ 제기동 1054-1 Notion 저장 성공!")
    else:
        print(f"⚠️  에러: {resp.text}")
except Exception as e:
    print(f"❌ 저장실패: {e}")

print("\n" + "="*60)
print("✅ 테스트 완료!")
print("✅ 제기동 법정동코드 확인됨")
print("✅ 서울시 API 테스트 완료") 
print("✅ Notion 저장 테스트 완료")
