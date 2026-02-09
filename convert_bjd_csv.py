import pandas as pd
import json
import os
import glob

print("🔄 법정동 CSV → **올바른 구이름:코드** 딕셔너리")

csv_files = glob.glob("*법정동*.csv") + glob.glob("*.csv")
csv_file = csv_files[0] if csv_files else None

if not csv_file:
    print("❌ CSV 파일 없음")
    exit(1)

print(f"✅ {csv_file}")

# 다중 인코딩
for enc in ['utf-8', 'cp949', 'euc-kr']:
    try:
        df = pd.read_csv(csv_file, encoding=enc)
        print(f"✅ {enc} 성공! {len(df)}행")
        break
    except:
        continue

# ✅ **핵심 수정: 시도명+시군구명 → 법정동코드 (앞10자리)**
bjd_dict = {}
for _, row in df.iterrows():
    sido = str(row.get('시도명', '')).strip()
    sigungu = str(row.get('시군구명', '')).strip()
    bjd_code = str(row.get('법정동코드', ''))[:10]
    
    if sido and sigungu and bjd_code:
        key = f"{sido} {sigungu}".strip()
        if key not in bjd_dict:
            bjd_dict[key] = bjd_code

print(f"\n🎉 **올바른 형식** 변환 완료! {len(bjd_dict)}개")

# 콘솔 출력 (복사해서 사용)
print("\n📋 **korea_bjd_codes.py 내용 (복사!):")
print("```python")
print("# 🇰🇷 대한민국 전국 법정동코드 (구이름:코드)")
print("KOREA_BJD_CODES =")
print(json.dumps(bjd_dict, ensure_ascii=False, indent=2))
print("```")

# 파일 저장
with open('korea_bjd_codes.py', 'w', encoding='utf-8') as f:
    f.write("# 🇰🇷 대한민국 전국 법정동코드 (구이름:코드)\n")
    f.write(f"# 총 {len(bjd_dict)}개 시군구\n\n")
    f.write("KOREA_BJD_CODES = ")
    json.dump(bjd_dict, f, ensure_ascii=False, indent=4)
    f.write("\n")

print("\n✅ korea_bjd_codes.py 재생성 완료!")
print("🚀 **올바른 형식**: '서울특별시 강남구': '1168000000'")
