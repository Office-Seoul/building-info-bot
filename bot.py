import requests

print("🚀 실제 역삼동 건물 테스트")
SEOUL_API_KEY = "6a4f504d5175737438355251754858"

# 더 넓은 범위 검색 (perPage=10)
url = "https://api.odcloud.kr/api/ConstructionInformationService/v1/getConstInfo"
params = {
    "serviceKey": SEOUL_API_KEY,
    "page": 1,
    "perPage": 10,  # 10개
    "cond[bjdCode::EQ]": "11680",  # 강남구
    "cond[dongNm::EQ]": "역삼1동"  # 역삼1동으로 변경
}

try:
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    
    buildings = data.get('data', [])
    print(f"📊 역삼1동 건물: {len(buildings)}개")
    
    for i, b in enumerate(buildings[:3], 1):
        print(f"{i}. {b.get('bldNm', 'N/A')} ({b.get('mainPurpsNm', 'N/A')})")
        
    print("✅ 실제 건물 데이터 확인 완료!")
    
except Exception as e:
    print(f"❌ 오류: {e}")
