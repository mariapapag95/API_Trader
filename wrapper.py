import json
import requests

def lastprice(ticker_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    return json.loads(requests.get(endpoint).text)['LastPrice']

def info(ticker_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    all_ = json.loads(requests.get(endpoint).text)
    #all_ = list(all_.values())
    #name = all_[1]
    #symbol = all_[2]
    #lastprice = all_[3]
    #marketcap = all_[8]
    #volume = all_[9]
    #high = all_[12]
    #low = all_[13]
    #open_ = all_[14]
    #info__ = [name, symbol, lastprice, marketcap,volume,high,low,open_]
    #return info__
    return all_

def name(ticker_symbol):
    endpoint = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol='+ticker_symbol
    return json.loads(requests.get(endpoint).text)['Name']
