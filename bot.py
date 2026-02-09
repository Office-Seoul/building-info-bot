import requests
import re
from notion_client import Client
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# GitHub Secrets에서 자동 로드
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
SEOUL_API_KEY = os.getenv("SEOUL_API_KEY")

notion = Client(auth=NOTION_TOKEN)

def get_building_id_from_url(notion_url):
    """노션 URL에서 페이지 ID 추출"""
    match = re.search(r'p=([a-zA-Z0-9-]+)', notion_url)
    return match.group(1).replace('-', '') if match else None

def fetch_seoul_building(address):
    """서울시 건축물대장 API 호출"""
    # 주소에서 동 이름 파싱 (예: "서울 강남구 역삼동")
    dong_match = re.search(r'([가-힣]+구.*?동)', address)
    if not dong_match:
        return {"status": "error", "message": "동 이름 파싱 실패"}
    
    dong = dong_match.group(1)
    
    # 서울시 건축물대장 API (11680=강남구 예시)
    url = f"https://api.seoul.go.kr:8088/openapi/buildingInfo/json/{SEOUL_API_KEY}/1/5/11680/{dong}"
    
    try:
        print(f"🌐 API 호출: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        building_list = data.get('buildingInfo', [])
        if building_list:
            item = building_list[0]
            return {
                "status": "success",
                "건물명": item.get('bdNm', '알수없음'),
                "주용도": item.get('mainPurpsNm', '알수없음'),
                "연면적": float(item.get('totArea', 0) or 0),
                "지상층수": int(item.get('totFlrCnt', 0) or 0),
                "지하층수": int(item.get('basFlrCnt', 0) or 0),
                "승강기수": int(item.get('elvtCnt', 0) or 0),
                "준공일자": item.get('cmpltYmd', '')[:10] if item.get('cmpltYmd') else '',
                "구조": item.get('strct', '알수없음')
            }
    except Exception as e:
        return {"status": "error", "message": f"API 오류: {str(e)}"}
    
    return {"status": "nodata", "message": "해당 동에 건물 정보 없음"}

def update_building_page(page_id, building_data):
    """노션 페이지 업데이트"""
    properties = {
        "api_상태": {
            "select": {"name": building_data.get("status", "error")}
        },
        "업데이트일": {
            "date": {"start": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        }
    }
    
    if building_data.get("status") == "success":
        properties.update({
            "건물명": {
                "title": [{"text": {"content": building_data.get("건물명", "알수없음")}}]
            },
            "주용도": {
                "select": {"name": building_data.get("주용도", "알수없음")}
            },
            "연면적_㎡": {
                "number": building_data.get("연면적", 0)
            },
            "지상층수": {
                "number": building_data.get("지상층수", 0)
            },
            "지하층수": {
                "number": building_data.get("지하층수", 0)
            },
            "승강기수": {
                "number": building_data.get("승강기수", 0)
            },
            "준공일자": {
                "date": {"start": building_data.get("준공일자", "")}
            },
            "전체구조": {
                "rich_text": [{"text": {"content": building_data.get("구조", "알수없음")}}]
            }
        })
    
    try:
        notion.pages.update(page_id=page_id, properties=properties)
        print("✅ 노션 업데이트 성공")
        return True
    except Exception as e:
        print(f"❌ 노션 업데이트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    page_url = os.getenv("PAGE_URL", "")
    if not page_url:
        print("❌ PAGE_URL 환경변수 필요")
        return 1
    
    page_id = get_building_id_from_url(page_url)
    if not page_id:
        print("❌ 유효하지 않은 노션 페이지 URL")
        return 1
    
    print(f"🔄 처리중: {page_url}")
    print(f"📄 페이지 ID: {page_id}")
    
    # 노션 페이지에서 주소 가져오기
    try:
        page = notion.pages.retrieve(page_id)
        address_prop = page['properties'].get('주소', {})
        
        if address_prop.get('title') and address_prop['title']:
            address = address_prop['title'][0]['text']['content']
        else:
            print("❌ '주소' 속성에 데이터 없음")
            return 1
            
        print(f"📍 주소: {address}")
    except Exception as e:
        print(f"❌ 노션 페이지 읽기 실패: {e}")
        return 1
    
    # 서울시 API 호출
    building_data = fetch_seoul_building(address)
    print(f"📊 API 결과: {building_data['status']}")
    
    # 노션 업데이트
    if update_building_page(page_id, building_data):
        print("✅ 전체 프로세스 완료!")
        return 0
    else:
        print("❌ 업데이트 실패")
        return 1

if __name__ == "__main__":
    exit(main())
