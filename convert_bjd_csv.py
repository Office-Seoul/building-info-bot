import pandas as pd
import json

print("🔄 법정동 CSV → Python 딕셔너리 자동 변환")

# 1. CSV 다운로드 후 업로드
df = pd.read_csv('국토교통부_전국_법정동.csv', encoding='cp949')

# 2. 시군구명 → 법정동코드 딕셔너리 생성
bjd_dict = {}
for _, row in df.iterrows():
    sigungu = row['시군구명']
    bjd_code = str(row['법정동코드'])[:10]  # 앞 10자리
    if sigungu not in bjd_dict:
        bjd_dict[sigungu] = bjd_code

# 3. Python 파일 자동 생성
with open('korea_bjd_codes.py', 'w', encoding='utf-8') as f:
    f.write("# 🇰🇷 대한민국 전국 법정동코드 (공공데이터포털 공식)\n")
    f.write("KOREA_BJD_CODES = ")
    json.dump(bjd_dict, f, ensure_ascii=False, indent=4)
    f.write("\n\nprint(f'✅ {len(bjd_dict)}개 법정동코드 로드 완료')")

print(f"✅ {len(bjd_dict)}개 법정동코드 → korea_bjd_codes.py 생성 완료!")
