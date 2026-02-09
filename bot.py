import requests
import urllib.parse

print("🚀 서울시 공식 건축물대장 API")
SEOUL_API_KEY = "6a4f504d5175737438355251754858"

# 서울시 공식 건축물대장 API (확실히 데이터 있음)
url = "https://openapt.seoul.go.kr:8586/api/getAptList"
params = {
    "key": SEOUL_API_KEY,
    "adm_sect_cd": "11680",  # 강남구
    "bjdong_nm": "역삼동"
}

print("🌐 서울시 아파트 정보 API 호출...")
try:
    r = requests.get(url, params=params, timeout=10)
    print(f"✅ 응답: {r.status_code}")
    data = r.json()
    
    if data.get('aptList', []):
        apt = data['aptList'][0]
        print(f"✅ 아파트: {apt.get('aptNm', 'N/A')}")
        print(f"✅ 주소: {apt.get('jibunAddr', 'N/A')}")
        print("🎉 서울시 공식 API 완벽!")
    else:
        print("ℹ️ 아파트 정보 없음")
        
except Exception as e:
    print(f"❌ 오류: {e}")
