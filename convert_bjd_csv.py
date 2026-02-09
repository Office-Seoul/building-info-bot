import pandas as pd
import json
import os
import glob

print("🔄 법정동 CSV 자동 변환 (파일명 무시)")

# 📁 모든 CSV 파일 자동 검색
csv_pattern = "*법정동*.csv"
csv_files = glob.glob(csv_pattern)
csv_files.extend(glob.glob("*.csv"))  # 모든 CSV

print(f"🔍 발견된 CSV: {csv_files}")

if not csv_files:
    print("❌ CSV 파일 없음. 다음 중 하나 업로드:")
    print("📥 https://www.data.go.kr/data/15063424/fileData.do")
    exit(1)

csv_file = csv_files[0]
print(f"✅ 자동 선택: {csv_file}")

# 🔧 다중 인코딩 자동 처리
encodings = ['utf-8', 'cp949', 'euc-kr', 'latin1']
df = None

for enc in encodings:
    try:
        print(f"📖 {enc} 시도...")
        df = pd.read_csv(csv_file, encoding=enc, low_memory=False)
        print(f"✅ {enc} 성공! {len(df)}행")
        break
    except:
        continue

if df is None:
    print("❌ 모든 인코딩 실패")
    exit(1)

# 📊 컬럼 자동 분석
print("📋 컬럼:", list(df.columns))
code_cols = [col for col in df.columns if '코드' in col or 'code' in col.lower()]
name_cols = [col for col in df.columns if '법정동' in col or '동명' in col or '시군구' in col]

print(f"🔍 코드컬럼: {code_cols}")
print(f"🔍 이름컬럼: {name_cols}")

# 기본 컬럼 선택
code_col = code_cols[0] if code_cols else df.columns[0]
name_col = name_cols[0] if name_cols else df.columns[-1]

print(f"사용: {code_col}, {name_col}")

# 딕셔너리 생성
bjd_dict = {}
for _, row in df.iterrows():
    try:
        name = str(row[name_col]).strip()
        code = str(row[code_col])[:10].strip()
        if name and code and name not in bjd_dict:
            bjd_dict[name] = code
    except:
        continue

# Python 파일 저장
with open('korea_bjd_codes.py', 'w', encoding='utf-8') as f:
    f.write("# 🇰🇷 전국 법정동코드 (자동 변환)\n")
    f.write(f"KOREA_BJD_CODES = {json.dumps(bjd_dict, ensure_ascii=False, indent=2)}\n")

print(f"🎉 ✅ 변환완료! {len(bjd_dict)}개 코드")
print("🚀 korea_bjd_codes.py 생성됨!")
