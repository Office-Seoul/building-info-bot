import pandas as pd
import json
import os

print("🔄 공공데이터포털 법정동 CSV → Python 딕셔너리 자동 변환")

# 📁 실제 파일명으로 수정 (UTF-8 깨짐 방지)
csv_files = [
    "국토교통부_전국 법정동_20250807.csv",
    "국토교통부_전국_법정동.csv",
    "전국_법정동.csv"
]

csv_file = None
for filename in csv_files:
    if os.path.exists(filename):
        csv_file = filename
        break

if not csv_file:
    print("❌ CSV 파일을 찾을 수 없습니다!")
    print("📥 다음 파일 중 하나를 다운로드 후 루트에 업로드:")
    for f in csv_files:
        print(f"  - {f}")
    print("🔗 https://www.data.go.kr/data/15063424/fileData.do")
    exit(1)

print(f"✅ {csv_file} 발견!")

# 🔧 다중 인코딩 자동 감지 (cp949 → euc-kr → utf-8 → latin1)
encodings = ['cp949', 'euc-kr', 'utf-8', 'latin1']

df = None
for encoding in encodings:
    try:
        print(f"📖 {encoding}으로 읽기 시도...")
        df = pd.read_csv(csv_file, encoding=encoding, low_memory=False)
        print(f"✅ {encoding} 성공! {len(df)}행")
        break
    except UnicodeDecodeError:
        print(f"❌ {encoding} 실패")
        continue

if df is None:
    print("❌ 모든 인코딩 실패. 파일을 확인해주세요.")
    exit(1)

# 🔍 컬럼 확인 (실제 컬럼명 파악)
print("📋 컬럼:", list(df.columns))
print("📊 샘플 데이터:")
print(df.head(3))

# 📝 딕셔너리 생성 (일반적인 컬럼명들 자동 감지)
print("🔄 딕셔너리 변환 중...")
bjd_dict = {}

common_columns = ['법정동코드', '법정동코드명', '법정동명', '시군구코드', '시도코드']

code_col = None
sigungu_col = None

for col in df.columns:
    col_lower = col.lower()
    if any(code in col_lower for code in ['법정동코드', '법정동코드명', '법정동코드']):
        code_col = col
    if any(sg in col_lower for sg in ['시군구', '시군구명']):
        sigungu_col = col

# 기본 컬럼명 사용
if not code_col:
    code_col = '법정동코드'
if not sigungu_col:
    sigungu_col = '시군구명'

print(f"🔍 사용 컬럼: 코드={code_col}, 시군구={sigungu_col}")

for _, row in df.iterrows():
    try:
        sigungu = str(row.get(sigungu_col, '')).strip()
        bjd_code = str(row.get(code_col, ''))[:10].strip()
        
        if sigungu and bjd_code and sigungu not in bjd_dict:
            bjd_dict[sigungu] = bjd_code
    except:
        continue

# 💾 Python 파일 생성
print("💾 korea_bjd_codes.py 생성...")
with open('korea_bjd_codes.py', 'w', encoding='utf-8') as f:
    f.write("# 🇰🇷 대한민국 전국 법정동코드 (공공데이터포털 공식)\n")
    f.write("# 출처: https://www.data.go.kr/data/15063424/fileData.do\n")
    f.write(f"# 총 {len(bjd_dict)}개 시군구 → 법정동코드 매핑\n\n")
    f.write("KOREA_BJD_CODES = ")
    json.dump(bjd_dict, f, ensure_ascii=False, indent=4)
    f.write("\n\n")
    f.write("# 사용법 예시:\n")
    f.write("# bjd_code = KOREA_BJD_CODES.get('서울특별시 강남구', '11680')\n")
    f.write(f"# print(f'강남구 법정동코드: {{bjd_code}}')\n")

print(f"🎉 ✅ 변환 완료!")
print(f"📊 총 {len(bjd_dict)}개 법정동코드 저장")
print("🚀 korea_bjd_codes.py 사용 준비 완료!")
print("\n📋 다음 단계: `python bot.py` 실행")
