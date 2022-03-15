import winsound
import ccxt
import pandas as pd
import config
from ta.trend import EMAIndicator,MACD,CCIIndicator
from ta.momentum import RSIIndicator,StochRSIIndicator
from ta.volatility import bollinger_mavg
from binance.client import Client
import keyboard
import pyautogui

#değerlerin alınması
#slowEMAValue = input("Yavaş Ema: ")
#fastEMAValue = input("Hızlı Ema: ")
pozisyondami = False
shortPozisyonda = False
longPozisyonda = False
alinacak_miktar = 0
zarar_edildi=2
kar_miktari=1.5
unrealizedProfit = 0
leverage=25
index=855
#coin = input("lütfen coin giriniz: ")
#coin =coin.upper()
client = Client(config.apiKey, config.secretKey)
exchange_info = client.get_exchange_info()
allCoins = []
coins = []
cout=0
arraylen=0
symbol = 'BTCUSDT'
coin_bulundu=True
# API CONNECT
exchange = ccxt.binance({
    "apiKey": config.apiKey,
    "secret": config.secretKey,

    'options': {
        'defaultType': 'future'
    },
    # ban yememek için geçilen bir parametre
    'enableRateLimit': True,
})
markets = exchange.load_markets()
for i in markets:
    #markets[i]["id"]=='BTCUSDT':
    if markets[i]["quoteId"]=='USDT':

        allCoins.append(markets[i]["id"])
        coins.append(markets[i])
        arraylen = len(allCoins)
print("Toplam coin sayısı: ", arraylen)

while True:
    try:
        balance = exchange.fetch_balance()
        trades = exchange.fetch_my_trades(symbol)
        free_balance = exchange.fetch_free_balance()
        positions = balance['info']['positions']
        current_positions = [position for position in positions if
                             float(position['positionAmt']) != 0 and position['symbol'] == symbol]
        position_bilgi = pd.DataFrame(current_positions,
                                      columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet",
                                               "positionAmt", "positionSide"])
        if not position_bilgi.empty:
            coin_bulundu=False
            print("paranın durumu: ", unrealizedProfit)
        else:
            coin_bulundu=True

        if coin_bulundu==True:
            if cout < arraylen-1:
                cout = cout + 1
                print("cout: ",cout)
                print("array len: ",arraylen)
                print("şuan taranan sıra: ",cout , " coin: ",symbol)
                print("serbest USDT: ",free_balance["USDT"])
                symbol = allCoins[cout]
            if arraylen-1 == cout:
                print("bütün elemanlar gezildi başa dönülüyor...")
                cout = 0
        # LOAD BARS
        #minutes bars
        minute_bars = exchange.fetch_ohlcv(symbol=symbol, timeframe='1m', since=None,limit=1500)
        df_minute_bars = pd.DataFrame(minute_bars,columns=["timestamp", "open", "high", "low", "close", "volume"])
        volume=df_minute_bars["volume"][len(df_minute_bars.index) - 1]
        print(volume)
        #three minutes bars
        three_minutes_bars =exchange.fetch_ohlcv(symbol=symbol, timeframe='3m', since=None,limit=1500)
        df_three_minutes_bars = pd.DataFrame(three_minutes_bars,columns=["timestamp", "open", "high", "low", "close", "volume"])
        #five minutes bars
        five_minutes_bars =exchange.fetch_ohlcv(symbol=symbol, timeframe='5m', since=None,limit=1500)
        df_five_minutes_bars = pd.DataFrame(five_minutes_bars,columns=["timestamp", "open", "high", "low", "close", "volume"])
        #15 minutes bars
        fifteen_minutes_bars = exchange.fetch_ohlcv(symbol=symbol, timeframe='15m', since=None,limit=1500)
        df_fifteen_minutes_bars = pd.DataFrame(fifteen_minutes_bars,columns=["timestamp", "open", "high", "low", "close", "volume"])
        #1 hour bars
        one_hour_bars = exchange.fetch_ohlcv(symbol=symbol, timeframe='1h', since=None,limit=1500)
        df_one_hour_bars = pd.DataFrame(one_hour_bars,columns=["timestamp", "open", "high", "low", "close", "volume"])
        #4 hours bars
        four_hours_bars = exchange.fetch_ohlcv(symbol=symbol, timeframe='4h', since=None, limit=1500)
        df_four_hours_bars = pd.DataFrame(four_hours_bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
        # day bars
        day_bars = exchange.fetch_ohlcv(symbol=symbol, timeframe='1d', since=None, limit=1500)
        df_day_bars = pd.DataFrame(day_bars, columns=["timestamp", "open", "high", "low", "close", "volume"])

        #load slow ma
        #4 saatlik
        slow_MA = bollinger_mavg(df_four_hours_bars["close"],50)
        df_four_hours_bars["Slow MA"]=slow_MA
        #load fast ma
        #4 saatlik
        fast_MA = bollinger_mavg(df_four_hours_bars["close"],200)
        df_four_hours_bars["Fast MA"] = fast_MA

        #fast ma nın bulunması
        son_fast_ma = df_four_hours_bars["Fast MA"][len(df_four_hours_bars.index)-1]
        #slow ma nın bulunması
        son_slow_ma =  df_four_hours_bars["Slow MA"][len(df_four_hours_bars.index)-1]

        #load Slow EMA
        # 1 dakikalık slow EMA
        slow_EMA = EMAIndicator(df_minute_bars["close"],50)
        df_minute_bars["Slow Ema"] = slow_EMA.ema_indicator()
        #3 dakikalık slow EMA
        slow_EMA = EMAIndicator(df_three_minutes_bars["close"], 50)
        df_three_minutes_bars["Slow Ema"] = slow_EMA.ema_indicator()
        #5 dakikalık slow EMA
        slow_EMA = EMAIndicator(df_five_minutes_bars["close"], 50)
        df_five_minutes_bars["Slow Ema"] = slow_EMA.ema_indicator()
        #15 dakikalık slow EMA
        slow_EMA = EMAIndicator(df_fifteen_minutes_bars["close"],50)
        df_fifteen_minutes_bars["Slow Ema"] = slow_EMA.ema_indicator()


        #load Fast EMA
        #1 dakikalık
        fast_EMA = EMAIndicator(df_minute_bars["close"], 13)
        df_minute_bars['Fast Ema'] = fast_EMA.ema_indicator()
        #3 dakikalık
        fast_EMA = EMAIndicator(df_three_minutes_bars["close"], 13)
        df_three_minutes_bars['Fast Ema'] = fast_EMA.ema_indicator()
        #5 dakikalık
        fast_EMA = EMAIndicator(df_five_minutes_bars["close"], 13)
        df_five_minutes_bars['Fast Ema'] = fast_EMA.ema_indicator()
        #15 saatlik
        fast_EMA = EMAIndicator(df_fifteen_minutes_bars["close"],13)
        df_fifteen_minutes_bars['Fast Ema'] = fast_EMA.ema_indicator()

        #fast emaların belirlenmesi
        #1 dakikalık fast ema
        one_minutes_son_fast_ema = df_minute_bars["Fast Ema"][len(df_minute_bars.index) - 1]
        one_minutes_sondan_birinci_fast_ema = df_minute_bars["Fast Ema"][len(df_minute_bars.index) - 2]
        one_minutes_sondan_ikinci_fast_ema = df_minute_bars["Fast Ema"][len(df_minute_bars.index) - 3]

        #3 dakikalık fast ema
        three_minutes_son_fast_ema = df_three_minutes_bars["Fast Ema"][len(df_three_minutes_bars.index) - 1]
        three_minutes_sondan_birinci_fast_ema = df_three_minutes_bars["Fast Ema"][len(df_three_minutes_bars.index) - 2]
        three_minutes_sondan_ikinci_fast_ema = df_three_minutes_bars["Fast Ema"][len(df_three_minutes_bars.index) - 3]

        #5 dakikalık fast ema
        five_minutes_son_fast_ema = df_five_minutes_bars["Fast Ema"][len(df_five_minutes_bars.index) - 1]
        five_minutes_sondan_birinci_fast_ema = df_five_minutes_bars["Fast Ema"][len(df_five_minutes_bars.index) - 2]
        five_minutes_sondan_ikinci_fast_ema = df_five_minutes_bars["Fast Ema"][len(df_five_minutes_bars.index) - 3]

        #15 dakikalık fast ema
        fiftenn_minutes_son_fast_ema = df_fifteen_minutes_bars["Fast Ema"][len(df_fifteen_minutes_bars.index)-1]
        fiftenn_minutes_sondan_birinci_fast_ema = df_fifteen_minutes_bars["Fast Ema"][len(df_fifteen_minutes_bars.index)-2]
        fiftenn_minutes_sondan_ikinci_fast_ema = df_fifteen_minutes_bars["Fast Ema"][len(df_fifteen_minutes_bars.index)-3]

        #slow emaların belirlenmesi
        # 1 dakikalık fast ema
        one_minutes_son_slow_ema = df_minute_bars["Slow Ema"][len(df_minute_bars.index) - 1]
        one_minutes_sondan_birinci_slow_ema = df_minute_bars["Slow Ema"][len(df_minute_bars.index) - 2]
        one_minutes_sondan_ikinci_slow_ema = df_minute_bars["Slow Ema"][len(df_minute_bars.index) - 3]
        # 3 dakikalık fast ema
        three_minutes_son_slow_ema = df_three_minutes_bars["Slow Ema"][len(df_three_minutes_bars.index) - 1]
        three_minutes_sondan_birinci_slow_ema = df_three_minutes_bars["Slow Ema"][len(df_three_minutes_bars.index) - 2]
        three_minutes_sondan_ikinci_slow_ema = df_three_minutes_bars["Slow Ema"][len(df_three_minutes_bars.index) - 3]
        # 5 dakikalık fast ema
        five_minutes_son_slow_ema = df_five_minutes_bars["Slow Ema"][len(df_five_minutes_bars.index) - 1]
        five_minutes_sondan_birinci_slow_ema = df_five_minutes_bars["Slow Ema"][len(df_five_minutes_bars.index) - 2]
        five_minutes_sondan_ikinci_slow_ema = df_five_minutes_bars["Slow Ema"][len(df_five_minutes_bars.index) - 3]
        #15 dakikalık saatlik
        fiftenn_minutes_son_slow_ema = df_fifteen_minutes_bars["Slow Ema"][len(df_fifteen_minutes_bars.index) - 1]
        fiftenn_minutes_sondan_birinci_slow_ema = df_fifteen_minutes_bars["Slow Ema"][len(df_fifteen_minutes_bars.index) - 2]
        fiftenn_minutes_sondan_ikinci_slow_ema = df_fifteen_minutes_bars["Slow Ema"][len(df_fifteen_minutes_bars.index) - 3]

        #ema farklarının mutlağının bulunması
        one_minutes_ema_farklari = one_minutes_son_fast_ema - one_minutes_son_slow_ema
        one_minutes_ema_farklari = abs(one_minutes_ema_farklari)
        threee_minutes_ema_farklari=three_minutes_sondan_birinci_fast_ema - three_minutes_sondan_birinci_slow_ema
        threee_minutes_ema_farklari = abs(threee_minutes_ema_farklari)
        five_minutes_ema_farklari=five_minutes_sondan_birinci_fast_ema - five_minutes_sondan_birinci_slow_ema
        five_minutes_ema_farklari = abs(five_minutes_ema_farklari)
        fiftenn_minutes_ema_farklari=fiftenn_minutes_sondan_birinci_fast_ema - fiftenn_minutes_sondan_birinci_slow_ema
        fiftenn_minutes_ema_farklari = abs(fiftenn_minutes_ema_farklari)
        #print("mutlak ema farkı: ",mutlak_ema_farklari)
        #RSI değerlerinin bulunması
        #rsi 35 ile 65 sınırları
        #dakikaklık
        rsi_value = RSIIndicator(df_minute_bars["close"], window=30)
        df_minute_bars["Slow RSI"] = rsi_value.rsi()
        son_rsi = df_minute_bars["Slow RSI"][len(df_minute_bars.index) - 1]


        #MACD Değerlerinin bulunması
        # 4 saatlik
        MACD_value = MACD(df_fifteen_minutes_bars["close"],window_slow=26,window_fast=33,window_sign=15)
        df_fifteen_minutes_bars["MACD SIGNAL"] = MACD_value.macd_signal()
        df_fifteen_minutes_bars["MACD DIFF"] = MACD_value.macd_diff()
        df_fifteen_minutes_bars["MACD"] = MACD_value.macd()
        son_MACD = df_fifteen_minutes_bars["MACD"][len(df_fifteen_minutes_bars.index) - 1]
        son_MACD_signal = df_fifteen_minutes_bars["MACD SIGNAL"][len(df_fifteen_minutes_bars.index) - 1]
        son_MACD_diff = df_fifteen_minutes_bars["MACD DIFF"][len(df_fifteen_minutes_bars.index) - 1]


        #CCI değerlerinin bulunması
        # 1 dakikalık
        CCI_Value=CCIIndicator(high=df_minute_bars["high"],low=df_minute_bars["low"],close=df_minute_bars["close"],window=50)
        df_minute_bars["CCI"]=CCI_Value.cci()
        #-185 ile + 185 arasında değişiyor
        son_CCI = df_minute_bars["CCI"][len(df_minute_bars.index) - 1]


        # Pozisyonda olup olmadığını kontrol etme
        if not position_bilgi.empty and position_bilgi["positionAmt"][len(position_bilgi.index) - 1] != 0:
            print("pozisyondamı:",pozisyondami)
            pozisyondami = True
            coin_bulundu=False
        else:
            coin_bulundu=True
            pozisyondami = False
            shortPozisyonda = False
            longPozisyonda = False


        # Long pozisyonda mı?
        if pozisyondami and float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) > 0:
            longPozisyonda = True
            shortPozisyonda = False
            coin_bulundu=False

        # Short pozisyonda mı?
        if pozisyondami and float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) < 0:
            shortPozisyonda = True
            longPozisyonda = False
            coin_bulundu=False

        #long Enter
        def longEnter(alinacak_miktar):
            print(coins[cout]['symbol'] ," Long enter")
            order = exchange.create_market_buy_order(coins[cout]['symbol'] , alinacak_miktar)
            print("\a")
            coin_bulundu==False



        # LONG EXIT
        def longExit():
            print(coins[cout]['symbol'] ," Long exit")
            order = exchange.create_market_sell_order(coins[cout]['symbol'], float(
                position_bilgi["positionAmt"][len(position_bilgi.index) - 1]), {"reduceOnly": True})
            print("\a")
            coin_bulundu==False




        #short enter
        def shortEnter(alinacak_miktar):
            print(coins[cout]['symbol'] ," short enter")
            order = exchange.create_market_sell_order(coins[cout]['symbol'] , alinacak_miktar)
            print("\a")
            coin_bulundu==False


        # short çık
        def shortExit():
            print(coins[cout]['symbol'] ," short exit")
            order = exchange.create_market_buy_order(coins[cout]['symbol'],
                    float(position_bilgi["positionAmt"][len(position_bilgi.index) - 1]) * -1, {"reduceOnly": True})
            print("\a")
            coin_bulundu==False


        alinacak_miktar = (float(free_balance["USDT"]) * float(leverage)) / float(
            df_minute_bars["close"][len(df_minute_bars.index) - 1])
        print(alinacak_miktar)
        #short gir
        if (one_minutes_son_fast_ema > one_minutes_son_slow_ema \
                and three_minutes_sondan_birinci_fast_ema > three_minutes_sondan_birinci_slow_ema \
                and five_minutes_sondan_birinci_fast_ema > five_minutes_sondan_birinci_slow_ema \
                and fiftenn_minutes_sondan_birinci_fast_ema < fiftenn_minutes_sondan_birinci_slow_ema) \
                and one_minutes_ema_farklari > threee_minutes_ema_farklari > five_minutes_ema_farklari \
                and shortPozisyonda == False:
            coin_bulundu=False
            alinacak_miktar = ((float(free_balance["USDT"])) * float(leverage)) / float(
                df_minute_bars["close"][len(df_minute_bars.index) - 1])
            if longPozisyonda:
                print(coins[cout]," LONG İŞLEMDEN ÇIKILIYOR...")
                longExit()
            print(coins[cout]," SHORT İŞLEME GİRİLİYOR...")
            shortEnter(alinacak_miktar)

        #long gir
        # and son_CCI <= -180  \
        # and son_rsi <= 37 \
        if  (one_minutes_son_fast_ema < one_minutes_son_slow_ema \
                and three_minutes_sondan_birinci_fast_ema < three_minutes_sondan_birinci_slow_ema \
                and five_minutes_sondan_birinci_fast_ema < five_minutes_sondan_birinci_slow_ema \
                and fiftenn_minutes_sondan_birinci_fast_ema>fiftenn_minutes_sondan_birinci_slow_ema)\
                and one_minutes_ema_farklari>threee_minutes_ema_farklari>five_minutes_ema_farklari \
                and longPozisyonda == False :

            alinacak_miktar = ((float(free_balance["USDT"])) * float(leverage)) / float(
                df_minute_bars["close"][len(df_minute_bars.index) - 1])
            coin_bulundu=False
            if shortPozisyonda:
                print(coins[cout]['symbol']," SHORT İŞLEMDEN ÇIKILIYOR...")
                shortExit()

            print(coins[cout]['symbol']," LONG İŞLEME GİRİLİYOR...")
            longEnter(alinacak_miktar)

        #alınacak miktarın hesaplanması
        alinacak_miktar = (((float(free_balance["USDT"]) / 100) * 100) * float(leverage)) / float(
            df_minute_bars["close"][len(df_minute_bars.index) - 1])
        #işlem varsa
        if not  position_bilgi.empty:
            unrealizedProfit=position_bilgi["unrealizedProfit"][len(position_bilgi.index) - 1]
            unrealizedProfit=float(unrealizedProfit)
        if unrealizedProfit < -0.15 and shortPozisyonda:
            zarar_edildi=zarar_edildi+1
            if zarar_edildi>1:
                kar_miktari=1
            print(coins[cout]['symbol']," zarar önleniyor short pozisyondan çıkılıyor...")
            coin_bulundu==False
            shortExit()
        if unrealizedProfit < -0.15 and longPozisyonda:
            zarar_edildi=zarar_edildi+1
            if zarar_edildi>1:
                kar_miktari=1
            print(coins[cout]['symbol']," zarar önleniyor long pozisyondan çıkılıyor...")
            coin_bulundu==False
            longExit()
        if unrealizedProfit >= 0.5  and shortPozisyonda:
            print(coins[cout]['symbol']," kar alınıyor short pozisyondan çıkılıyor...")
            coin_bulundu==False
            shortExit()
        if unrealizedProfit >= 0.5 and longPozisyonda :
            print(coins[cout]['symbol'],",kar alınıyor long pozisyondan çıkılıyor...")
            longExit()

        if pozisyondami == False:
            print("POZİSYON ARANIYOR...",symbol)
        if shortPozisyonda:
            print(symbol," SHORT POZİSYONDA BEKLİYOR...",free_balance["USDT"])
            coin_bulundu=False
        if longPozisyonda:
            print(symbol," LONG POZİSYONDA BEKLİYOR...",free_balance["USDT"])
            coin_bulundu=False

    except ccxt.BaseError as Error:
        print("hata alınan coin..." ,allCoins[cout]," ",coins[cout]['symbol'] )
        #allCoins.remove(allCoins[cout-1])0
        #coins.remove(coins[cout-1])
        #arraylen=arraylen-1
        print("[ERROR] ", Error)
        continue

