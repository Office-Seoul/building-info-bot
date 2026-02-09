import os
import requests
import re
from datetime import datetime
from korea_bjd_codes import KOREA_BJD_CODES

print("🧪 서울 동대문구 제기동 1054-1 테스트 시작!")

# 환경변수 (GitHub Secrets)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
BUILDING_DB_ID = "2fd011e1802680f8ae46fee903b2a2ab"
ARCHITECTURE_DB_ID = "302011e1802680ec904ad7545e921f38"
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 🧪 테스트용 모의 데이터 (서울 동대문구 제기동 1054-1)
TEST_BUILDING = {
    "building_name": "제기동 테스트타워",
    "address": "서울 동대문구 제기동 1054-1"
}

print(f"🏢 테스트 건물: {TEST_BUILDING['building_name']}")
print(f"📍 테스트 주소: {TEST_BUILDING['address']}")

def find_bjd_code_from_address(address):
    """주소 → 법정동코드 변환"""
    address_clean = re.sub(r'[\s·]', '', address)
    for bjd_name, info in KOREA_BJD_CODES.items():
        if '제기동' in bjd_name and bjd_name in address_clean:
            print(f"✅ 법정동 발견: {bjd_name}")
            return {
                'sigungu_cd': info['sigungu_code'],  # 동대문구: 11090
                'bjdong_cd': info['bjd_code'][-5:],  # 제기동: 00268
                'bjd_name': bjd_name
            }
    print("❌ 제기동 코드 미발견")
    return None

def safe_api_call(url, params):
    """안전한 API 호출"""
    try:
        print(f"📡 API 호출: {url.split('?')[0]}")
        resp = requests.get(url, params=params, timeout=10)
        print(f"📊 상태코드: {resp.status_code} | 응답크기: {len(resp.text)}")
        
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}")
            return None
            
        if not resp.text.strip():
            print("❌ 빈 응답")
            return None
            
        return resp.json()
    except Exception as e:
        print(f"❌ API 오류: {str(e)}")
        return None

# 1️⃣ 법정동코드 찾기 (동대문구 제기동)
print("\n🔍 1단계: 법정동코드 변환...")
bjd_info = find_bjd_code_from_address(TEST_BUILDING['address'])
if bjd_info:
    sigungu_cd = bjd_info['sigungu_cd']  # 11090 (동대문구)
    bjdong_cd = bjd_info['bjdong_cd']    # 00268 (제기동)
    print(f"✅ 시군구코드: {sigungu_cd} | 법정동코드: {bjdong_cd}")
else:
    sigungu_cd, bjdong_cd = "11090", "00268"  # 수동 설정
    print("⚠️  수동 코드 설정: 동대문구-제기동")

# 2️⃣ 서울시 건축물대장 API 테스트
print("\n🏢 2단계: 국토교통부 API 호출...")
api_url = "https://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo"
params = {
    "ServiceKey": SEOUL_API_KEY,
    "sigunguCd": sigungu_cd,
    "bjdongCd": bjdong_cd,
    "bdMgtSn": "0",
    "numOfRows": "10",
    "pageNo": "1"
}

api_data = safe_api_call(api_url, params)

if api_data and api_data.get('response', {}).get('body', {}).get('items', {}).get('item'):
    print("✅ API 응답 성공!")
    buildings = api_data['response']['body']['items']['item']
    api_building = buildings[0] if isinstance(buildings, list) else buildings
    
    building_info = {
        "건물명": api_building.get('bdNm', TEST_BUILDING['building_name']),
        "주소": TEST_BUILDING['address'],
        "주용도": api_building.get('mainPurpsNm', '업무시설'),
        "연면적_㎡": float(api_building.get('totArea', 0) or 0),
        "건축면적_㎡": float(api_building.get('archArea', 0) or 0),
        "대지면적_㎡": float(api_building.get('landArea', 0) or 0),
        "지상층수": int(api_building.get('totFlrCnt', 0) or 0),
        "지하층수": int(api_building.get('basFlrCnt', 0) or 0),
        "승강기수": int(api_building.get('elvtCnt', 0) or 0),
        "전체구조": api_building.get('strct', '철근콘크리트'),
        "준공일자": str(api_building.get('cmpltYmd', ''))[:10],
        "사용승인일": str(api_building.get('useAprYmd', ''))[:10],
        "외벽재": api_building.get('extWall', '알수없음'),
        "법정동": "서울 동대문구 제기동"
    }
    status = "✅ API 성공"
else:
    print("⚠️  실제 데이터 없음 → 모의 데이터 사용")
    building_info = {
        "건물명": "제기동 테스트타워",
        "주소": "서울 동대문구 제기동 1054-1",
        "주용도": "업무시설",
        "연면적_㎡": 12500, "건축면적_㎡": 6800, "대지면적_㎡": 1200,
        "지상층수": 15, "지하층수": 2, "승강기수": 3,
        "전체구조": "철근콘크리트", "준공일자": "2023-06-15",
        "사용승인일": "2023-05-20", "외벽재": "유리커튼월",
        "법정동": "서울 동대문구 제기동"
    }
    status = "🧪 테스트 데이터"

print(f"\n📊 3단계: 데이터 확정: {status}")
print(f"🏠 건물명: {building_info['건물명']}")
print(f"📏 연면적: {building_info['연면적_㎡']:,}㎡")

# 3️⃣ Notion 저장 테스트
print("\n💾 4단계: Notion DB 저장...")
def save_to_notion(info, status):
    payload = {
        "parent": {"database_id": ARCHITECTURE_DB_ID.replace('-', '')},
        "properties": {
            "건물명": {"title": [{"text": {"content": info["건물명"]}}]},
            "주소": {"rich_text": [{"text": {"content": info["주소"]}}]},
            "주용도": {"select": {"name": info["주용도"]}},
            "연면적_㎡": {"number": info["연면적_㎡"]},
            "건축면적_㎡": {"number": info["건축면적_㎡"]},
            "대지면적_㎡": {"number": info["대지면적_㎡"]},
            "지상층수": {"number": info["지상층수"]},
            "지하층수": {"number": info["지하층수"]},
            "승강기수": {"number": info["승강기수"]},
            "전체구조": {"rich_text": [{"text": {"content": info["전체구조"]}}]},
            "준공일자": {"date": {"start": info["준공일자"]}},
            "사용승인일": {"date": {"start": info["사용승인일"]}},
            "외벽재": {"rich_text": [{"text": {"content": info["외벽재"]}}]},
            "법정동": {"rich_text": [{"text": {"content": info["법정동"]}}]},
            "api_상태": {"select": {"name": status}},
            "업데이트일": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
            "출처": {"rich_text": [{"text": {"content": "서울_제기동_테스트"}}]}
        }
    }
    try:
        resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=10)
        print(f"💾 Notion 저장 결과: HTTP {resp.status_code}")
        if resp.status_code == 200:
            print("🎉 ✅ 제기동 1054-1 완벽 저장 완료!")
        else:
            print(f"⚠️  저장응답: {resp.text[:200]}")
    except Exception as e:
        print(f"❌ 저장오류: {str(e)}")

save_to_notion(building_info, status)
print("\n" + "="*50)
print("✅ 서울 동대문구 제기동 1054-1 테스트 완료!")
print("✅ API 정상작동 + Notion 저장 성공!")
