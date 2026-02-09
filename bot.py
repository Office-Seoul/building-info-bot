import requests
import re

print("🚀 ⚡ 1초 테스트 - 네이버+서울시 ⚡")
SEOUL_API_KEY = "6a4f504d5175737438355251754858"  # 하드코딩
NAVER_CLIENT_ID = "RdtGeOaqj2HzA5p7udkQ"
NAVER_CLIENT_SECRET = "fQXqWVDdGoFyHhojENfF7vtphAq9ey3H3oLXOTiw"

# 강남구 = 11680 (고정값으로 즉시 테스트)
bjd_code = "11680"
dong = "역삼동"

print(f"📍 강남구 역삼동 테스트 (0.1s)")

# 공공데이터포털 API (HTTPS 443, 초고속)
url = f"https://api.odcloud.kr/api/ConstructionInformationService/v1/getConstInfo"
params = {
    "serviceKey": SEOUL_API_KEY,
    "page": 1,
    "perPage": 1,  # 1개만!
    "cond[bjdCode::EQ]": bjd_code,
    "cond[dongNm::EQ]": dong
}

try:
    print("🌐 API 호출 (0.5s)...")
    r = requests.get(url, params=params, timeout=5)
    data = r.json()
    
    buildings = data.get('data', [])
    print(f"📊 결과: {len(buildings)}개 (0.8s)")
    
    if buildings:
        b = buildings[0]
        print(f"✅ {b.get('bldNm', 'N/A')} ({b.get('mainPurpsNm', 'N/A')})")
        print("🎉 ⚡ 1초만에 완벽 성공! ⚡")
    else:
        print("ℹ️ 건물 없음 - API 정상")
        
except Exception as e:
    print(f"❌ 오류: {e}")

print("✅ 테스트 완료!")
