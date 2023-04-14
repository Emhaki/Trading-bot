from django.shortcuts import render
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# binance 패키지
from binance.client import Client


# 바이낸스 API 문서
# https://binance-docs.github.io/apidocs/#change-log
# https://python-binance.readthedocs.io/en/latest/

# 네이버 주식 API
# https://finance.naver.com/item/main.nhn?code=005930 

def main(request):
    return render(request,'bot/main.html')

def get_stock_summery(itemcode):
    tem_info = requests.get('https://finance.naver.com/item/main.nhn?code='+ itemcode)
    stock_info = tem_info.json()
    return stock_info

class CoinBot:
    API_KEY = os.getenv("API_KEY")
    API_SECRET = os.getenv("SECRET_KEY")
    # {'symbol': 'BTCUSDT', 'priceChange': '792.58000000', 'priceChangePerce0', 'bidPrice': '30773.95000000', 'bidQty': '0.06166600', 'askPrice': 
    # '30773.96000000', 'askQty': '0.01169800', 'openPrice': '29981.37000000', 'highPrice': '31509.06000000', 'lowPrice': '29213.34000000', 'volume': '4083.33534300', 'quoteVolume': '123563779.67891466', 'openTime': 
    # 1681348566185, 'closeTime': 1681434966185, 'firstId': 1489511, 'lastId': 1691560, 'count': 202050}
    def __init__(self):
        self.client = Client(self.API_KEY, self.API_SECRET, testnet=True)
    
    # 지정가에 코인 구매
    def buy_coin_at_discount(self, symbol, quantity):
        # 1. 코인의 지금 가격을 불러오기
        # 2. 코인의 지금 가격에서 10% 디스카운트 된 가격을 계산하기
        # 3. 그 가격에 주문 넣기

        # 1
        ticker_into = self.client.get_ticker(symbol=symbol)
        last_price = ticker_into['lastPrice'] # 30805.72000000
        
        # 2
        discounted_price = round((float(last_price) * 0.9), 2)

        # 3
        order = self.client.order_limit_buy(
            symbol = symbol,
            quantity = quantity,
            price = str(discounted_price)
        )
        return order

    # 현재가에 코인구매
    def buy_coin_at_market_price(self, symbol, quantity):
        order = self.client.order_market_buy(
            symbol = symbol,
            quantity = quantity
        )
        return order
        
bot = CoinBot()
bot.buy_coin_at_discount()
