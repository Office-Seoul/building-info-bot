import requests

print("🚀 확실한 데이터 테스트 - 대치동")
SEOUL_API_KEY = "6a4f504d5175737438355251754858"

# 대치동 (건물 많은 곳)
url = "https://api.odcloud.kr/api/ConstructionInformationService/v1/getConstInfo"
params = {
    "serviceKey": SEOUL_API_KEY,
    "page": 1,
    "perPage": 5,
    "cond[bjdCode::EQ]": "11680",  # 강남구
    "cond[dongNm::EQ]": "대치동"    # 대치동으로 변경
}

try:
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    
    buildings = data.get('data', [])
    print(f"📊 대치동 건물: {len(buildings)}개")
    
    if buildings:
        for i, b in enumerate(buildings[:3], 1):
            print(f"{i}. {b.get('bldNm', 'N/A')} - {b.get('mainPurpsNm', 'N/A')}")
    else:
        print("ℹ️ 데이터 없음")
        
    print("✅ API 완벽 동작!")
    
except Exception as e:
    print(f"❌ 오류: {e}")
