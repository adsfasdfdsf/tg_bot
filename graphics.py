import pandas as pd
import mplfinance as mpf
import time

def draw_price_graph(name, data, secid):
    open = []
    close = []
    high = []
    low = []
    dates = []
    print(data)
    for i in data:
        dates.append(pd.to_datetime(i[0]))
        open += [i[1]]
        close += [i[2]]
        high += [i[3]]
        low += [i[4]]
    a = {}
    a["Open"] = open
    a["Close"] = open
    a["High"] = open
    a["Low"] = open
    price_series = pd.DataFrame(a, index=dates)
    mpf.plot(price_series, type="line", style="binance", figratio=[15, 8], savefig=f"{secid}.png")

