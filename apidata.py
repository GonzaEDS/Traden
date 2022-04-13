import requests
import time
import copy
import json
import datetime


def api_call_data():

   # select api_key to use
   api_keys_list = ['460281c4-ceb3-47be-82b9-cf34912638a7',
                     'bc3c1627-fa9b-4a79-982a-7c2b1bb9fcb1', 'd1a61a2e-d26a-4ba3-88f0-e94c8cb52b91', '00abe0cc-0132-4322-b6fc-b8a56b80552c', 'e66f3842-7138-49e8-80bf-7f115f431ed5']

   for i in range(5):
      headers = {
            'X-CMC_PRO_API_KEY': api_keys_list[i],
            'Accepts': 'application/json'
      }

      info_key = 'https://pro-api.coinmarketcap.com/v1/key/info'

      credits_left = requests.get(info_key, headers=headers).json()['data']['usage']['current_day']['credits_left']

      if credits_left > 5:
         api_key = copy.deepcopy(api_keys_list[i])
         break

   with open("now.txt") as f:
      now = f.read()

      # if (int(datetime.datetime.now().minute) %60) > ((int(now)+2) %60):
      if int(datetime.datetime.now().minute) != int(now):
         with open("now.txt","w") as now_file:
            now_file.write(str(datetime.datetime.now().minute))

      headers = {
         'X-CMC_PRO_API_KEY': api_key,
         'Accepts': 'application/json'

         }

      with open('data.txt') as json_file:
         data = json.load(json_file)

      numbers = '1'
      for row in data['data'][1:]:
         numbers += ','+ str(row['id'])

      info_url = f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info?id={numbers}'
      latest_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=100&convert=USD'

      json_info = requests.get(info_url, headers=headers).json()
      json_latest = requests.get(latest_url, headers=headers).json()

      info = copy.deepcopy(json_info)
      data = copy.deepcopy(json_latest)

      #update info files
      with open('info.txt', 'w') as outfile:
         json.dump(info, outfile)
      with open('data.txt', 'w') as outfile:
         json.dump(data, outfile)

      with open('data.txt') as json_file:
         data = json.load(json_file)

      with open('info.txt') as json_file:
         info = json.load(json_file)

      coins = []
      for row in data['data']:
         coin_dict = {}
         sym = row['symbol']
         Id = row['id']
         coin_dict['id'] = Id
         coin_dict['logo'] = info['data'][f'{Id}']['logo']
         coin_dict['symbol'] = row['symbol']
         coin_dict['name'] = row['name']
         coin_dict['price'] = str(round(row['quote']['USD']['price'], 5))
         coins.append(coin_dict)

      return coins