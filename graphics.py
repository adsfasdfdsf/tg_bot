import pandas as pd
import mplfinance as mpf


async def draw_price_graph(name, data, secid):
    opened = []
    close = []
    high = []
    low = []
    dates = []
    ind = []
    print(data)
    for i in data:
        print(i)
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
    print(df)
    ticklocations = [df.index.get_loc(tick) for tick in df.index][::2]
    axlist[-2].xaxis.set_ticks(ticklocations)
    axlist[-2].set_xticklabels(ind[::2])
    fig.savefig(f"{secid}.png")



