import pandas as pd
from yahoo_fin import stock_info as si
from datetime import date, timedelta

def analysis_lt(share_list):
    ret_l = pd.DataFrame(columns=["change", "pos", "indi"])
    for share in share_list:
        market = None
        if share[-2:] == "NS":
            market = "^NSEI"
        elif share[-2:] == "BO":
            market = "BSE-500.BO"
        tdy = date.today()
        sdy = tdy - timedelta(days = 1851)
        hist = si.get_data(market, start_date= sdy, interval= "1d").close.to_frame()
        hist_comp = si.get_data(share, start_date= sdy, interval= "1d").close.to_frame()
        hist_comp = hist_comp.tail(15)
        hist_comp ["close"] = hist_comp.close.__round__(3)
        hist.columns = ["close"]
        hist ["date"] = hist.index
        hist_comp ["inx"] = range(1, 16, 1)
        hist_comp = hist_comp.set_index("inx")
        hist ["ma200"] = hist.close.ewm(span=200).mean()
        tdyma = hist.tail(1)
        tdy_close = float(hist.iat[-1, 0]).__round__(3)
        dma200 = float(tdyma.ma200).__round__(3)
        change = [0] * 14
        pos = 0
        neg = 0
        for i in range(1, 15, 1):
            change[i - 1] = float(hist_comp.close[i + 1] - hist_comp.close[i])
            if (change[i - 1] >= 0):
                pos = pos + change[i - 1]
            else:
                neg = neg + change[i - 1]
        neg = -neg / 14
        pos = pos / 14
        rs = pos / neg
        rsi = (100 - (100 / (1 + rs))).__round__(3)
        x = False
        y = False
        if (dma200 < tdy_close):
            if (rsi <= 30):
                x = True
                y = False
                ret_l = ret_l.append({"change" : x, "pos" : y,"indi": rsi}, ignore_index=True)
            elif (rsi >= 70):
                x = True
                y = True
                ret_l = ret_l.append({"change": x, "pos": y, "indi": rsi}, ignore_index=True)
            else:
                x = False
                y = False
                ret_l = ret_l.append({"change": x, "pos": y, "indi": rsi}, ignore_index=True)
        elif (dma200 > tdy_close):
            if (rsi >= 70):
                x = True
                y = True
                ret_l = ret_l.append({"change": x, "pos": y, "indi": rsi}, ignore_index=True)
            else:
                x = False
                y = False
                ret_l = ret_l.append({"change": x, "pos": y, "indi": rsi}, ignore_index=True)
        else:
            ret_l = ret_l.append({"change": x, "pos": y, "indi": rsi}, ignore_index=True)
    print(ret_l)
    return ret_l.to_json(orient='records')

def analysis_st(share_list, save_list, delta_list):
    ret_s = pd.DataFrame(columns=["share_n", "timestamp", "w", "x"])
    lent = len(share_list)
    n = 0
    for m in range (0, lent, 1):
        share = share_list[m]
        delta = delta_list[m]
        save = save_list[m]
        tdy = date.today()
        ydy = date.today() - timedelta(days=1)
        sdy = date.today() - timedelta(days=1500)
        dma50 = si.get_data(share, start_date=sdy, end_date=tdy, interval="1d").close.to_frame()
        dma50["ma"] = dma50.close.rolling(window=50).mean()
        dma50 = dma50.tail(1)
        dma50.index = [0]
        ma50 = dma50.at[0, "ma"]
        hist = si.get_data(share, start_date=tdy, interval="1m").close.to_frame()
        hist ["timestamp"] = hist.index + timedelta (minutes=330)
        hist ["ticker"] = si.get_data(share, start_date=tdy, interval="1m").ticker
        hist = hist.tail(15)
        hist.index = range(0, 15, 1)
        w = False
        x = False
        for i in range(0, 14, 1):
            mini = save - delta
            maxi = save + delta
            cur_price = si.get_live_price(share)
            if cur_price >= maxi:
                w = True
                x = True
                n = int(n)
                ret_s.at [n, "w"] = w
                ret_s.at [n, "x"] = x
                ret_s.at [n, "share_n"] = int(m)
                ret_s.at[n, "timestamp"] = hist.at[i, "timestamp"]
                n = n + 1
                break
            elif cur_price <= mini:
                w = True
                x = False
                ret_s.at[n, "w"] = w
                ret_s.at[n, "x"] = x
                ret_s.at[n, "share_n"] = int(m)
                ret_s.at[n, "timestamp"] = hist.at[i, "timestamp"]
                n = n + 1
                break
        n = n
    print(ret_s)
    return ret_s.to_json(orient='records')

analysis_lt(["RELIANCE.NS", "TATAMOTORS.BO", "AXISBANK.BO"])
analysis_st(["RELIANCE.NS", "TATAMOTORS.BO", "AXISBANK.BO"], [1994.00, 300.00, 680.00], [15, 5, 20])