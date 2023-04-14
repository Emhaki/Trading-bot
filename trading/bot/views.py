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
    print(stock_info)
    return stock_info

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("SECRET_KEY")
client = Client(API_KEY, API_SECRET, testnet=True)
print(client.get_account())