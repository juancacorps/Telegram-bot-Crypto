import requests
import lxml.html as html
import datetime
import pandas as pd

# xpath expression and url
URL_CRYPTO_INFORMATION = 'https://coinmarketcap.com/es/'
XPATH_NAME_CRYPTO = '//td//p[@class="sc-1eb5slv-0 iJjGCS"]/text()'
XPATH_SIMBOL_CRYPTO = '//td//p[@class="sc-1eb5slv-0 gGIpIK coin-item-symbol"]/text()'
XPATH_PRICEUSD_CRYPTO = '//td//div[@class="price___3rj7O "]/a/text()'
XPATH_CAPIMAKET_CRYPTO = '//td//p[@class="sc-1eb5slv-0 kDEzev"]/text()'
XPATH_USD_TO_GTQ = '//p[@class="result__BigRate-sc-1bsijpp-1 iGrAod"]/text()[1]'
URL_CURRENCY_CHANGE = 'https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=GTQ'
# Your credencials of Telegram
ID_USER_TELEGRAM = 'XXX'
BOT_TOKEN = 'XXXXX'

# ID or USER_NAME of contacts of Telegram
CONTACTS = {'Andrea Rogiron' : 'XXXXX',
            'Juan Carlos Ortega' : 'XXXXX',
            'Checo Perez' : 'XXXXX',
            'Leo Dan' : 'XXXXX',
            'Timmy Torner' : 'XXXXX'}

def extract_crypto_data():
    response = requests.get(URL_CRYPTO_INFORMATION)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        parsed = html.fromstring(content)
        crypto_names =  parsed.xpath(XPATH_NAME_CRYPTO)
        crypto_simbols =  parsed.xpath(XPATH_SIMBOL_CRYPTO)
        crypto_prices_usd = parsed.xpath(XPATH_PRICEUSD_CRYPTO)
        crypto_capimarket = parsed.xpath(XPATH_CAPIMAKET_CRYPTO)
        # Create Dataframe
        dataframe = pd.DataFrame({ 
        'Crytocurrency':crypto_names,
        'Symbol':crypto_simbols,
        'Price $':crypto_prices_usd,
        'Market Cap':crypto_capimarket,
        'Date':datetime.date.today()})
        transform_cryto_data(dataframe)
    else:
        print(f'Error {response.status_code} in the response')


def transform_cryto_data(dataframe):
    response = requests.get(URL_CURRENCY_CHANGE)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        parsed = html.fromstring(content)
        currency_gtq = parsed.xpath(XPATH_USD_TO_GTQ)
        currency_gtq = float(currency_gtq[0])
        #Clean and transform dataframe
        dataframe['Dollar Value'] = currency_gtq
        dataframe['Price $'] = dataframe['Price $'].apply(lambda x: round(float(x.replace('$','').replace(',','')),2))
        dataframe['Price GTQ'] = round(dataframe['Price $'] * dataframe['Dollar Value'],2)
        dataframe.convert_dtypes().dtypes
        path = f'reports/cryto {datetime.date.today()}.xlsx'
        dataframe.to_excel(path,index=False)

        send_file_to_telegram(path)
    else:
         print(f'Error {response.status_code} in the response')


def send_file_to_telegram(path_file):
    message = f'''
  Hello, good morning, this is the price update of the most popular cryptocurrencies. 
  Programmed with much love: @juancacorps :)'''

    for name in CONTACTS.keys():
         send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + CONTACTS[name] + '&parse_mode=Markdown&text=' + message
         response = requests.get(send_text)
         print(response.status_code)
         send_document = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendDocument?chat_id=' + CONTACTS[name]
         files = [('document', open(path_file,'rb'))]
         response_file = requests.request('POST', send_document, headers={}, data = {}, files = files)
         print(response_file.status_code)

if __name__ == '__main__':
    extract_crypto_data()