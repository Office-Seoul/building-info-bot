import os
import requests
from datetime import datetime

print("🚀 주소만 넣으면 3초만에 건축물대장 자동입력")

# GitHub Secrets (이미 설정됨)
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN") 
ARCHITECTURE_DB_ID = "302011e1802680ec904ad7545e921f38"

# 테스트 주소 (여기만 바꾸면 됨!)
ADDRESS = "서울 동대문구 제기동 1054"  # 번지 생략 = 전체 조회
SIGUNGU_CD = "11090"  # 동대문구
BJDONG_CD = "00268"   # 제기동

headers_notion = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

print(f"🔍 {ADDRESS} 건축물대장 조회...")

# 1️⃣ API 호출 (가장 간단한 방법)
url = "https://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo"
params = {
    "ServiceKey": SEOUL_API_KEY,
    "sigunguCd": SIGUNGU_CD,
    "bjdongCd": BJDONG_CD,
    "numOfRows": "5",
    "pageNo": "1"
}

try:
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    
    if data['response']['body']['totalCount'] > 0:
        building = data['response']['body']['items']['item'][0]
        print("✅ 실시간 데이터 수집 완료!")
        
        # 2️⃣ Notion 저장 (최소 속성만)
        payload = {
            "parent": {"database_id": ARCHITECTURE_DB_ID.replace('-', '')},
            "properties": {
                "건물명": {"title": [{"text": {"content": building.get('bdNm', '알수없음')}}]},
                "주소": {"rich_text": [{"text": {"content": ADDRESS}}]},
                "주용도": {"select": {"name": building.get('mainPurpsNm', '알수없음')}},
                "연면적_㎡": {"number": float(building.get('totArea', 0))},
                "지상층수": {"number": int(building.get('totFlrCnt', 0))},
                "준공일자": {"date": {"start": str(building.get('cmpltYmd', ''))[:10]}},
                "api_상태": {"select": {"name": "✅실시간API"}},
                "업데이트일": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            }
        }
        
        notion_resp = requests.post("https://api.notion.com/v1/pages", 
                                  headers=headers_notion, json=payload)
        
        if notion_resp.status_code == 200:
            print("🎉 ✅ Notion 자동입력 완료!")
        else:
            print(f"❌ Notion: {notion_resp.status_code}")
            
    else:
        print("⚠️ 해당 주소에 건물 없음")
        
except Exception as e:
    print(f"❌ 오류: {e}")
    print("💡 SEOUL_API_KEY 확인")
