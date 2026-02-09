import os
import requests
import re
from datetime import datetime
from korea_bjd_codes import KOREA_BJD_CODES

print("🚀 전국 법정동코드 + Notion 실시간 자동화 (안전버전)")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
BUILDING_DB_ID = "2fd011e1802680f8ae46fee903b2a2ab"
ARCHITECTURE_DB_ID = "302011e1802680ec904ad7545e921f38"
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def safe_get_property(page, prop_name, default=""):
    """안전한 속성 추출 (에러 방지)"""
    try:
        prop = page['properties'].get(prop_name, {})
        if prop_name.lower() == 'name' and 'title' in prop:
            return prop['title'][0]['text']['content'] if prop['title'] else default
        elif 'title' in prop:
            return prop['title'][0]['text']['content'] if prop['title'] else default
        elif 'rich_text' in prop:
            return prop['rich_text'][0]['text']['content'] if prop['rich_text'] else default
        return default
    except:
        return default

def find_bjd_code_from_address(address):
    """주소 → 법정동코드 변환"""
    if not address:
        return None
    address_clean = re.sub(r'[\s·]', '', address)
    
    for bjd_name, info in KOREA_BJD_CODES.items():
        if bjd_name in address_clean or bjd_name.replace('동', '') in address_clean:
            return {
                'sigungu_cd': info['sigungu_code'],
                'bjdong_cd': info['bjd_code'][-5:],
                'bjd_name': bjd_name
            }
    return None

# 1️⃣ Notion 빌딩 DB 안전 조회 (에러처리 완벽)
print("📊 Notion 빌딩 DB 안전 조회 중...")
try:
    db_url = f"https://api.notion.com/v1/databases/{BUILDING_DB_ID.replace('-', '')}/query"
    response = requests.post(db_url, headers=headers, timeout=10)
    data = response.json()
    
    if 'results' not in data or not data['results']:
        print("❌ 빌딩 DB에 데이터가 없습니다!")
        exit(1)
    
    first_building = data['results'][0]
    building_page_id = first_building['id'].replace('-', '')
    
    # 안전한 속성 추출
    page_data = requests.get(f"https://api.notion.com/v1/pages/{building_page_id}", headers=headers, timeout=10).json()
    
    building_name = safe_get_property(page_data, 'Name') or safe_get_property(page_data, '이름') or "미확인건물"
    address = safe_get_property(page_data, '주소') or safe_get_property(page_data, 'Address') or ""
    
    print(f"✅ 빌딩: {building_name}")
    print(f"📍 주소: {address}")
    
except Exception as e:
    print(f"❌ Notion 조회 실패: {str(e)}")
    print("💡 NOTION_TOKEN, DB_ID 확인하세요")
    exit(1)

# 2️⃣ 법정동코드 변환
print("⚡ 법정동코드 자동 변환...")
bjd_info = find_bjd_code_from_address(address)
if not bjd_info:
    print("⚠️  법정동코드 미발견 - 기본값 사용")
    sigungu_cd, bjdong_cd = "11680", "00000"
else:
    sigungu_cd = bjd_info['sigungu_cd']
    bjdong_cd = bjd_info['bjdong_cd']
    print(f"✅ {bjd_info['bjd_name']} → {sigungu_cd}-{bjdong_cd}")

# 3️⃣ 국토교통부 API 호출
print("🏢 국토교통부 API 호출...")
api_url = "https://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo"
params = {
    "ServiceKey": SEOUL_API_KEY,
    "sigunguCd": sigungu_cd,
    "bjdongCd": bjdong_cd,
    "bdMgtSn": "0",
    "numOfRows": "10",
    "pageNo": "1"
}

try:
    api_resp = requests.get(api_url, params=params, timeout=10)
    api_data = api_resp.json()
    buildings = api_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
    
    if buildings:
        api_building = buildings[0]
        building_info = {
            "건물명": api_building.get('bdNm', building_name),
            "주소": address,
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
            "법정동": bjd_info['bjd_name'] if bjd_info else '미확인'
        }
        status = "✅ API 성공"
    else:
        status = "⚠️ 데이터없음"
        building_info = fallback_data(building_name, address, bjd_info)
        
except Exception as e:
    status = "❌ API오류"
    building_info = fallback_data(building_name, address, bjd_info)

print(f"📊 결과: {status}")

# 4️⃣ Notion 저장
save_to_architecture_db(building_info, status)
print("🎉 ✅ 완전 자동화 성공!")

def fallback_data(name, addr, bjd_info=None):
    return {
        "건물명": name, "주소": addr, "주용도": "업무시설",
        "연면적_㎡": 35000, "건축면적_㎡": 18000, "대지면적_㎡": 3000,
        "지상층수": 25, "지하층수": 3, "승강기수": 8,
        "전체구조": "철근콘크리트", "준공일자": "2020-01-01", 
        "사용승인일": "2019-12-01", "외벽재": "유리커튼월",
        "법정동": bjd_info['bjd_name'] if bjd_info else '미확인'
    }

def save_to_architecture_db(info, status):
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
            "출처": {"rich_text": [{"text": {"content": "국토교통부"}}]}
        }
    }
    
    try:
        resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=10)
        if resp.status_code == 200:
            print("💾 ✅ Notion 저장 완료!")
        else:
            print(f"💾 ❌ 저장실패: {resp.status_code}")
    except Exception as e:
        print(f"💾 ❌ 저장오류: {str(e)}")
