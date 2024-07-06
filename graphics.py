import matplotlib.pyplot as mpl
import mplfinance as mpf
import pandas as pd


async def draw_price_graph(name: str, data: list, secid: str) -> None:
    opened = []
    close = []
    high = []
    low = []
    dates = []
    ind = []
    for i in data:
        ind += [i[0]]
        dates.append(pd.to_datetime(i[0]))
        opened += [i[1]]
        close += [i[2]]
        high += [i[3]]
        low += [i[4]]
    a = {}
    a["Open"] = opened
    a["Close"] = close
    a["High"] = high
    a["Low"] = low
    df = pd.DataFrame(a, index=dates)
    fig, axlist = mpf.plot(df, type="line", style="binance", figratio=[17, 8], figscale=1.2, fontscale=0.7, tight_layout=True,
                           returnfig=True, xrotation=90, title=f"{name} • {secid} • price in Rub")
    ticklocations = [df.index.get_loc(tick) for tick in df.index][::2]
    axlist[-2].xaxis.set_ticks(ticklocations)
    axlist[-2].set_xticklabels(ind[::2])
    fig.savefig(f"{secid}.png")
    fig.clf()


async def draw_payment_graph(ticker: str, data: list, name: str) -> None:
    a = {}
    for i in data:
        if i[2]:
            a[i[1]] = i[2]
    series = pd.Series(a)
    mpl.title(f"{name} • {ticker}\nIN {data[0][-1]}")
    mpl.bar(series.index, height=series)
    mpl.xticks(rotation=45)
    mpl.yticks(series.values)
    mpl.savefig(f"{ticker}payment.png")

