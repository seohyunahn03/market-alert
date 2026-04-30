import yfinance as yf
import requests
from datetime import datetime
import pytz

# 🚨 여기에 본인이 만든 채널명을 꼭 다시 적어주세요!
NTFY_CHANNEL = "taehwan_vix_alert_2026" 

def get_market_data():
    vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    
    # 봇(Bot) 차단을 막기 위해 일반 브라우저처럼 위장하는 부분 (수정 완료!)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://edition.cnn.com/'
    }
    
    response = requests.get(url, headers=headers).json()
    fng_score = response['fear_and_greed']['score']
    fng_rating = response['fear_and_greed']['rating']
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
