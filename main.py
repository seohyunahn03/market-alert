import yfinance as yf
import requests
import fear_greed
from datetime import datetime
import pytz

# 🚨 본인의 ntfy 채널명 확인 (따옴표 필수!)
NTFY_CHANNEL = "taehwan_vix_alert_2026" 

def get_market_data():
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
    fng_data = fear_greed.get()
    fng_score = fng_data['score']
    fng_rating = fng_data['rating']
    return round(vix, 2), round(fng_score), fng_rating

# 💡 나만의 3단계 투자 전략 로직
def get_strategy_message(vix, fng_score):
    # 3. 스나이퍼 매수 (VIX 40 이상 역사적 패닉)
    if vix >= 40.0:
        return "🎯 [역사적 패닉! 스나이퍼 매수]\n- 행동: 남은 누적 현금 100% 전액 소진!\n- 설명: 모두가 끝났다고 도망칠 때입니다. 이때 투입된 현금이 훗날 자산의 앞자리를 바꿔줍니다."
        
    # 3. 스나이퍼 매수 (극도의 공포)
    elif vix >= 30.0 or fng_score < 25:
        return "🎯 [패닉장! 스나이퍼 매수]\n- 행동: 남은 누적 현금의 50% 이상 과감하게 투입!\n- 설명: 훗날 자산의 앞자리를 바꿔줄 기회입니다."
        
    # 2. 1차 저점 매수 (조정장)
    elif vix >= 20.0 or fng_score < 45:
        return "📉 [조정장! 1차 저점 매수]\n- 행동: 당월 70만원 + 누적 현금의 30% 투입\n- 대상: 할인율 커진 '나스닥100 레버리지'나 '반도체' 집중 매수 (평단가 낮추기)"
        
    # 1. 현금 축적기 (평상시/상승장)
    else:
        return "💰 [평상시! 현금 축적기]\n- 행동: 당월 70만원 전액 파킹통장(CMA) 저축\n- 설명: ISA 160만원이 알아서 크도록 둡니다. 환호할 때 추가 매수는 낭비! 다음 기회를 위해 총알을 묵묵히 모으세요."

def send_push(title, message, priority="default", tags="chart_with_upwards_trend"):
    requests.post(f"https://ntfy.sh/{NTFY_CHANNEL}",
        data=message.encode('utf-8'),
        headers={
            "Title": title.encode('utf-8'),
            "Tags": tags,
            "Priority": priority
        })

def main():
    vix, fng_score, fng_rating = get_market_data()
    tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(tz)
    
    # 전략 메시지 불러오기
    strategy_msg = get_strategy_message(vix, fng_score)
    
    # 1. 아침 8시 정규 브리핑 (현재 지수 + 나의 행동 지침)
    if now.hour == 8:
        msg = f"[지수 요약]\nVIX: {vix} | 공포탐욕: {fng_score} ({fng_rating})\n\n{strategy_msg}"
        send_push("🌅 아침 증시 & 전략 브리핑", msg, tags="sunrise")
        
    # 2. 긴급 알림 (장이 열려있는 동안 VIX 30 이상 or 공포 25 미만 진입 시)
    if vix >= 30.0 or fng_score < 25:
        msg = f"[지수 요약]\nVIX: {vix} | 공포탐욕: {fng_score}\n\n{strategy_msg}"
        send_push("🚨 변동성 긴급 알림!", msg, priority="high", tags="warning")

if __name__ == "__main__":
    main()
