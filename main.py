import yfinance as yf
import requests
import fear_greed
from datetime import datetime
import pytz

# 🚨 본인이 만든 ntfy 채널명으로 반드시 변경해주세요! (예: taehwan_vix_alert_2026)
NTFY_CHANNEL = " taehwan_vix_alert_2026" 

def get_market_data():
    # VIX 지수 가져오기
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
    
    # CNN 차단 우회 전용 라이브러리 사용
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
    
    # 1. 매일 아침 8시(KST) 요약 브리핑
    if now.hour == 8:
        msg = f"오늘의 장 시작 전 요약입니다.\nVIX: {vix}\n공포탐욕: {fng_score} ({fng_rating})"
        send_push("🌅 아침 증시 브리핑", msg, tags="sunrise")
        
    # 2. VIX 30 이상 or 공포탐욕 25 이하 시 긴급 알림
    if vix >= 30.0 or fng_score <= 25:
        msg = f"🚨 시장 변동성 경고!\nVIX: {vix}\n공포탐욕: {fng_score} ({fng_rating})"
        send_push("📉 변동성 긴급 알림!", msg, priority="high", tags="warning")

if __name__ == "__main__":
    main()
