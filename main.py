import yfinance as yf
import requests
import fear_greed
from datetime import datetime
import pytz

# 🚨 여기에 본인의 ntfy 채널명을 다시 적어주세요! 
NTFY_CHANNEL = "taehwan_vix_alert_2026"

def get_market_data():
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
    
    # 새로운 전용 도구 사용 (이제 에러가 날 수 없는 구조입니다)
    fng_data = fear_greed.get()
    fng_score = fng_data['score']
    fng_rating = fng_data['rating']
    
    return round(vix, 2), round(fng_score), fng_rating

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
    
   if now.hour == 8: 
        msg = f"오늘의 장 시작 전 요약입니다.\nVIX: {vix}\n공포탐욕: {fng_score} ({fng_rating})"
        send_push("🌅 아침 증시 브리핑", msg, tags="sunrise")
        
    if vix >= 30.0 or fng_score <= 25:
        msg = f"🚨 시장 변동성 경고!\nVIX: {vix}\n공포탐욕: {fng_score} ({fng_rating})"
        send_push("📉 변동성 긴급 알림!", msg, priority="high", tags="warning")

if __name__ == "__main__":
    main()
