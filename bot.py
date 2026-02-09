import discord
from discord.ext import commands
import requests
import pandas as pd
import re
from korea_bjd_codes import KOREA_BJD_CODES

SERVICE_KEY = '공공데이터포털_서비스키'  # data.go.kr에서 발급
DISCORD_TOKEN = '디스코드봇토큰'

bot = commands.Bot(command_prefix='!', intents=commands.Intents.default())

@bot.event
async def on_ready():
    print(f'{bot.user} 연결 완료!')

@bot.command(name='조회')
async def building_info(ctx, *, address: str):
    await ctx.send(f'🔍 `{address}` 조회 중...')
    
    # 1단계: 주소에서 법정동코드 찾기
    bjd_info = find_bjd_code(address)
    if not bjd_info:
        await ctx.send('❌ 법정동을 찾을 수 없습니다. 정확한 주소를 입력해주세요.')
        return
    
    sigungu_cd = bjd_info['sigungu_cd']
    bjdong_cd = bjd_info['bjdong_cd']
    
    # 2단계: 건축물대장 API 호출 (총괄표제부)
    url = 'http://apis.data.go.kr/B553067/openapi/totalInfo'
    params = {
        'serviceKey': SERVICE_KEY,
        'sigunguCd': sigungu_cd,
        'bjdongCd': bjdong_cd,
        'numOfRows': 10,
        'pageNo': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        df = pd.read_xml(response.text)
        
        if not df.empty and len(df) > 0:
            result = f"🏠 **{address} 건축물 정보**\n"
            for idx, row in df.head(3).iterrows():
                result += f"• **{row.get('관리번호', 'N/A')}**\n"
                result += f"  용도: {row.get('주용도명', 'N/A')}\n"
                result += f"  구조: {row.get('건축구조명', 'N/A')}\n"
                result += f"  층수: {row.get('건축물동수', 'N/A')}동 {row.get('건축물층수', 'N/A')}층\n\n"
            await ctx.send(result)
        else:
            await ctx.send('❌ 해당 지역에 등록된 건축물 정보가 없습니다.')
            
    except Exception as e:
        await ctx.send(f'❌ 조회 실패: {str(e)[:100]}')

def find_bjd_code(address: str):
    """주소에서 법정동코드 찾기 (퍼지 매칭)"""
    address = address.replace(' ', '')
    
    for bjd_name, info in KOREA_BJD_CODES.items():
        if bjd_name in address or bjd_name.replace('동', '') in address:
            return {
                'sigungu_cd': info['sigungu_code'],
                'bjdong_cd': info['bjd_code'][-5:],  # 마지막 5자리
                'bjd_name': bjd_name
            }
    return None

bot.run(DISCORD_TOKEN)
