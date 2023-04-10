from django.shortcuts import render
import requests

# 사용자 관심 종목 추가
# 실시간 인기 종목 알아보기
# 종목의 시세 변동 알아보기

# 네이버 주식 API
# https://finance.naver.com/item/main.nhn?code=005930 
def main(request):
    return render(request,'bot/main.html')

def get_stock_summery(itemcode):
    tem_info = requests.get('https://finance.naver.com/item/main.nhn?code='+ itemcode)
    stock_info = tem_info.json()
    print(stock_info)
    return stock_info

