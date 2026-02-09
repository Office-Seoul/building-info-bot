import os
import requests

print("🚀 네이버지도 API 테스트")
print(f"✅ NAVER_CLIENT_ID: {'있음' if os.getenv('NAVER_CLIENT_ID') else '없음'}")
print(f"✅ NAVER_CLIENT_SECRET: {'있음' if os.getenv('NAVER_CLIENT_SECRET') else '없음'}")
print(f"✅ SEOUL_API_KEY: {'있음' if os.getenv('SEOUL_API_KEY') else '없음'}")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 네이버지도 Geocoding API 테스트
url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
headers = {
    "X-NCP-APIGW-API-KEY-ID": NAVER_CLIENT_ID,
    "X-NCP-APIGW-API-KEY": NAVER_CLIENT_SECRET
}
params = {
    "query": "서울 강남구 역삼동"
}

print("🌐 네이버지도 API 호출 중...")

try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    data = response.json()
    
    print(f"✅ 응답 코드: {response.status_code}")
    
    if data.get("status") == "OK" and data.get("addresses"):
        address_info = data["addresses"][0]
        print(f"✅ 주소: {address_info.get('roadAddress', 'N/A')}")
        print(f"✅ 좌표: {address_info.get('x')}, {address_info.get('y')}")
        print("🎉 네이버지도 API 완벽 동작!")
    else:
        print(f"❌ API 응답 오류: {data}")
        
except Exception as e:
    print(f"❌ 네이버 API 오류: {e}")

print("✅ 네이버지도 테스트 완료!")
