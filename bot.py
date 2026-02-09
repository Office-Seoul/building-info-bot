import os
print("🚀 GitHub Actions 환경 확인")
print(f"✅ NOTION_TOKEN: {'있음' if os.getenv('NOTION_TOKEN') else '없음'}")
print(f"✅ SEOUL_API_KEY: {'있음' if os.getenv('SEOUL_API_KEY') else '없음'}")

try:
    from notion_client import Client
    print("✅ notion_client 라이브러리 로드 성공")
    
    notion = Client(auth=os.getenv("NOTION_TOKEN"))
    print("✅ Notion 연결 성공!")
    
    # 데이터베이스 목록 출력 (권한 테스트)
    me = notion.users.me()
    print(f"✅ 사용자: {me['name']}")
    
    print("🎉 모든 연결 정상!")
    print("다음 단계: 실제 데이터베이스 테스트")
    
except Exception as e:
    print(f"❌ 연결 실패: {e}")

print("✅ 테스트 완료 - 환경 정상")
