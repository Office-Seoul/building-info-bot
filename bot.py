
### **💾 bot.py 완전 코드 (복사해서 붙여넣기)**

```python
import requests
import re
from notion_client import Client
import os
from datetime import datetime

# GitHub Secrets에서 자동 로드
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

notion = Client(auth=NOTION_TOKEN)

def get_building_id_from_url(notion_url):
    """노션 URL에서 페이지 ID 추출"""
    match = re.search(r'p=([a-zA-Z0-9]+)', notion_url)
    return match.group(1) if match else None

def fetch_seoul_building(address):
    """서울시 건축물대장 API 호출"""
    # 주소 파싱 (예: 서울 강남구 역삼동 123-45)
    dong_match = re.search(r'(\w+구.*?동)', address)
    if not dong_match:
        return {"status": "error", "message": "동 이름 파싱 실패"}
    
    dong = dong_match.group(1)
    
    # 서울시 표제부 API (실제 엔드포인트)
    url = f"https://api.seoul.go.kr:8088/openapi/buildingInfo/json/{SEOUL_API_KEY}/1/5/11680/{dong}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('buildingInfo', [{}]):
            item = data['buildingInfo']
            return {
                "status": "success",
                "건물명": item.get('bdNm', '알수없음'),
                "주용도": item.get('mainPurpsNm', '알수없음'),
                "연면적": float(item.get('totArea', 0)),
                "지상층수": int(item.get('totFlrCnt', 0)),
                "지하층수": int(item.get('basFlrCnt', 0)),
                "승강기수": int(item.get('elvtCnt', 0)),
                "준공일자": item.get('cmpltYmd', ''),
                "구조": item.get('strct', '')
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    return {"status": "nodata"}

def update_building_page(page_id, building_data):
    """건축물대장 페이지 업데이트"""
    properties = {
        "api_상태": {"select": {"name": building_data["status"]}},
        "업데이트일": {"date": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}}
    }
    
    if building_data["status"] == "success":
        properties.update({
            "건물명": {"title": [{"text": {"content": building_data["건물명"]}}]},
            "주용도": {"select": {"name": building_data["주용도"]}},
            "연면적_㎡": {"number": building_data["연면적"]},
            "지상층수": {"number": building_data["지상층수"]},
            "지하층수": {"number": building_data["지하층수"]},
            "승강기수": {"number": building_data["승강기수"]},
            "준공일자": {"date": {"start": building_data["준공일자"]}},
            "전체구조": {"rich_text": [{"text": {"content": building_data["구조"]}}]}
        })
    
    notion.pages.update(page_id=page_id, properties=properties)
    return True

def main():
    """GitHub Actions 실행"""
    page_url = os.getenv("PAGE_URL", "")
    if not page_url:
        print("❌ PAGE_URL 환경변수 필요")
        return
    
    page_id = get_building_id_from_url(page_url)
    if not page_id:
        print("❌ 페이지 ID 추출 실패")
        return
    
    print(f"🔄 처리중: {page_url}")
    
    # 빌딩정보 페이지에서 주소 가져오기
    page = notion.pages.retrieve(page_id)
    address_prop = page['properties'].get('주소', {})
    if not address_prop or not address_prop['title']:
        print("❌ 주소 속성 없음")
        return
    
    address = address_prop['title']['text']['content']
    print(f"📍 주소: {address}")
    
    # 건축물대장 API 호출
    building_data = fetch_seoul_building(address)
    print(f"📊 결과: {building_data['status']}")
    
    # 건축물대장 페이지 업데이트
    if update_building_page(page_id, building_data):
        print("✅ 업데이트 완료!")
    else:
        print("❌ 업데이트 실패")

if __name__ == "__main__":
    main()
