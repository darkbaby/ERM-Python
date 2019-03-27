# import requests
# import json
#
# class APIService:
#
#     def __init__(self):
#         pass
#
#
#     def getDataFromBOTAPI(self, refDate, currencyArray):
#         url = 'https://iapi.bot.or.th/Stat/Stat-ExchangeRate/DAILY_AVG_EXG_RATE_V1/'
#         refDateS = refDate.strftime('%Y-%m-%d')
#         headers = {'api-key' : 'U9G1L457H6DCugT7VmBaEacbHV9RX0PySO05cYaGsm'}
#
#         for i in currencyArray:
#
#             queryParams = {'start_period' : refDateS, 'end_period' : refDateS, 'currency' : i}
#             response = requests.request('GET', url, headers=headers, params=queryParams)
#             print(response.text)
#
#             jsonDecode = json.loads(response.text)
#
#             if jsonDecode['result']['success'] == 'true':
#                 if jsonDecode['result']['data']['data_detail'][0]['period'] == refDateS:
#                     buyingRate = jsonDecode['result']['data']['data_detail'][0]['buying_sight']
#                     sellingRate = jsonDecode['result']['data']['data_detail'][0]['selling']
#                     avgRate = jsonDecode['result']['data']['data_detail'][0]['mid_rate']
#                     print( i + ' ' + buyingRate + ' ' + sellingRate + ' ' + avgRate )