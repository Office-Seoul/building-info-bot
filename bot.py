import os
from notion_client import Client
import requests
import re
from datetime import datetime

notion = Client(auth=os.getenv("NOTION_TOKEN"))
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

def process_building_database(database_url):
    """데이터베이스 첫 번째 페이지 처리"""
    # 데이터베이스 ID 추출
    database_id = re.search(r'notion\.so/([a-z0-9]{32})', database_url)
    if not database_id:
        print("❌ 데이터베이스 ID 추출 실패")
        return False
    
    database_id = database_id.group(1)
    print(f"🔄 데이터베이스: {database_id}")
    
    # 데이터베이스 쿼리
    try:
        pages = notion.databases.query(database_id=database_id)
        if not pages['results']:
            print("❌ 데이터베이스 비어있음")
            return False
        
        first_page = pages['results'][0]
        page_id = first_page['id'].replace('%', '')
        print(f"📄 첫 번째 페이지: {page_id}")
        
        # 주소 가져오기
        page = notion.pages.retrieve(page_id)
        address_prop = page['properties'].get('주소', {})
        
        if address_prop.get('title') and address_prop['title']:
            address = address_prop['title'][0]['text']['content']
            print(f"📍 주소: {address}")
        else:
            print("❌ 주소 없음")
            return False
            
    except Exception as e:
        print(f"❌ 데이터베이스 오류: {e}")
        return False
    
    # 서울시 API 호출
    dong_match = re.search(r'([가-힣]+구.*?동)', address)
    if not dong_match:
        print("❌ 동 파싱 실패")
        return False
    
    dong = dong_match.group(1)
    url = f"https://api.seoul.go.kr:8088/openapi/buildingInfo/json/{SEOUL_API_KEY}/1/5/11680/{dong}"
    
    try:
        print(f"🌐 서울시 API: {dong}")
        response = requests.get(url, timeout=15)
        data = response.json()
        buildings = data.get('buildingInfo', [])
        
        if buildings:
            building = buildings[0]
            print(f"✅ 건물: {building.get('bdNm', '알수없음')}")
            
            # 페이지 업데이트
            notion.pages.update(
                page_id=page_id,
                properties={
                    "api_상태": {"select": {"name": "success"}},
                    "건물명": {"title": [{"text": {"content": building.get('bdNm', '알수없음')}}]},
                    "주용도": {"select": {"name": building.get('mainPurpsNm', '알수없음')}},
                    "업데이트일": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
                }
            )
            print("🎉 업데이트 완료!")
            return True
        else:
            print("❌ 건물 정보 없음")
            return False
            
    except Exception as e:
        print(f"❌ API 오류: {e}")
        return False

# 메인 실행
PAGE_URL = os.getenv("PAGE_URL", "https://www.notion.so/2fd011e1802680f8ae46fee903b2a2ab")
print(f"🚀 실행: {PAGE_URL}")

if process_building_database(PAGE_URL):
    print("✅ 완벽 성공!")
else:
    print("❌ 처리 실패")
