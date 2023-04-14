from django.shortcuts import render
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# binance 패키지
from binance.client import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
        ticker_into = self.client.get_ticker(symbol=symbol)
        last_price = ticker_into['lastPrice'] # 30805.72000000
        
        # 2. 코인의 지금 가격에서 10% 디스카운트 된 가격을 계산하기
        discounted_price = round((float(last_price) * 0.9), 2)

        # 3. 그 가격에 주문 넣기
        return self.client.order_limit_buy(
            symbol = symbol,
            quantity = quantity,
            price = str(discounted_price)
        )
        

    # 현재가에 코인구매
    def buy_coin_at_market_price(self, symbol, quantity):
        return self.client.order_market_buy(
            symbol = symbol,
            quantity = quantity
        )
        
    
    def sell_coin_at_primium(self, symbol, quantity):
        # 1. 코인의 현재 가격불러오기
        ticker_into = self.client.get_ticker(symbol=symbol)
        last_price = ticker_into['lastPrice'] # 30805.72000000
        
        # 2 코인에 지금 가격에서 10% 프리미엄 한 가격 계산
        primium_price = round((float(last_price) * 1.1), 2)

        # 3 그 가격에 주문 넣기
        return self.client.order_limit_sell(
            symbol = symbol,
            quantity = quantity,
            price = str(primium_price)
        )
        
    
    def cancel_all_open_orders(self):
        open_orders = self.client.get_open_orders()
        for order in open_orders:
            order_id = order['orderId']
            symbol = order['symbol']
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            print(result)

bot = CoinBot()
client = bot.client
# print(bot.client.get_open_orders())

def buy_coin_at_price(client, symbol, target_price):
    # symbol = BNBUSDT
    ticker_info = client.get_ticker(symbol=symbol)
    last_price = ticker_info['lastPrice']
    last_price = round(float(last_price), 2)
    if last_price <= target_price:
        return client.order_market_buy(
            symbol=symbol,
            quantity=1.0,
            price=str(target_price)
        )
    return None

# 1. 이동평균선 보다 낮으면 사기
# 2. 이동평균선 보다 가격이 높으면 팔기
def get_price_history(klines):
    klines = client.get_historical_klines('BNBUSDT', '1h', '2 week ago UTC')
    for line in klines:
        del line[5:]
    
    df = pd.DataFrame(klines, columns=['data', 'open', 'high', 'low', 'close'])
    df.set_index('data', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms')

    return df.astype(float)
# print(get_price_history(client))
#                        open    high     low  close
# data
# 2023-04-05 05:00:00  314.90  315.60  314.90  315.6
# 2023-04-05 06:00:00  315.60  315.80  315.00  315.5
# 2023-04-05 07:00:00  315.20  315.22  113.30  314.6
# 2023-04-05 08:00:00  314.70  314.90  313.86  314.9
# 2023-04-05 09:00:00  314.82  315.00  313.90  314.9
# ...                     ...     ...     ...    ...
# 2023-04-14 09:00:00  333.00  333.01  332.30  332.6
# 2023-04-14 10:00:00  332.60  333.60  244.84  332.2
# 2023-04-14 11:00:00  332.28  335.80  332.20  333.2
# 2023-04-14 12:00:00  333.30  334.80  250.20  331.6
# 2023-04-14 13:00:00  331.70  332.50  331.30  332.5

def trade_based_on_5_sms(client):
    df = get_price_history(client)

    # 5일 이동 평균선
    df['5_sma'] = df['close'].rolling(5).mean()
    df['buy'] = np.where(df['5_sma'] > df['close'], 1, 0) # 참이면 1, 거짓이면 0
    df['sell'] = np.where(df['5_sma'] <= df['close'], 1, 0) # 참이면 1, 거짓이면 0
    return df
print(trade_based_on_5_sms(client))
#                        open    high     low  close   5_sma  buy  sell
# data
# 2023-04-05 05:00:00  314.90  315.60  314.90  315.6     NaN    0     0 
# 2023-04-05 06:00:00  315.60  315.80  315.00  315.5     NaN    0     0 
# 2023-04-05 07:00:00  315.20  315.22  113.30  314.6     NaN    0     0 
# 2023-04-05 08:00:00  314.70  314.90  313.86  314.9     NaN    0     0 
# 2023-04-05 09:00:00  314.82  315.00  313.90  314.9  315.10    1     0 
# ...                     ...     ...     ...    ...     ...  ...   ... 
# 2023-04-14 09:00:00  333.00  333.01  332.30  332.6  333.44    1     0 
# 2023-04-14 10:00:00  332.60  333.60  244.84  332.2  333.14    1     0 
# 2023-04-14 11:00:00  332.28  335.80  332.20  333.2  332.98    0     1 
# 2023-04-14 12:00:00  333.30  334.80  250.20  331.6  332.50    1     0 
# 2023-04-14 13:00:00  331.70  332.80  331.30  332.6  332.44    0     1 

def trade_based_on_15_sms(client):
    df = get_price_history(client)

    # 이동 평균선
    df['5_sma'] = df['close'].rolling(5).mean()
    df['15_sma'] = df['close'].rolling(15).mean()
    
    return df

df = trade_based_on_15_sms(client)
df[['close', '5_sma', '15_sma']].plot()
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()