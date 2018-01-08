import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.stattools import adfuller
import pandas.tseries

def GETSQL(stock1, stock2, startdate, enddate):
    conn = pymysql.connect(host="localhost", user="root", passwd="password", db="invest")
    cursor = conn.cursor()
    sqlstr1 = "select `trade_date`, `close` from `stock_daily_Data` where `stock_code` = \"" + stock1 + "\" and (`trade_date` between \"" + startdate + "\" and \"" + enddate + "\");"
    cursor.execute(sqlstr1)
    data1 = cursor.fetchall()
    data1 = list(data1)
    data1 = [list(i) for i in data1]
    data1 = pd.DataFrame(data1)
    data1.columns = ["trade_date", "close"]

    sqlstr2 = "select `trade_date`, `close` from `stock_daily_Data` where `stock_code` = \"" + stock2 + "\" and (`trade_date` between \"" + startdate + "\" and \"" + enddate + "\");"
    cursor.execute(sqlstr2)
    data2 = cursor.fetchall()
    data2 = list(data2)
    data2 = [list(i) for i in data2]
    data2 = pd.DataFrame(data2)
    data2.columns = ["trade_date", "close"]

    return data1, data2

def CHART(stock1, stock2, data1, data2):
    plt.figure(figsize=(10, 8), dpi=80)
    plt.subplot(111)
    dates = data1["trade_date"]
    close_data1 = [float(i) for i in list(data1["close"])]
    close_data2 = [float(i) for i in list(data2["close"])]


    plt.plot(dates, close_data1, color="blue", linewidth=2.5, linestyle="-")
    plt.plot(dates, close_data2, color="red", linewidth=2.5, linestyle="-")

    #plt.ylim((0, 10))

    plt.xlabel(stock1)
    plt.ylabel(stock2)
    plt.title("Stock Prices Coef : " + str(np.corrcoef(data1["close"], data2["close"])[0, 1]))
    plt.show()

def STRATEGY(stock1, stock2, data1, data2):
    date = data1["trade_date"]
    data = data1["close"] - data2["close"]
    #print(data)
    #empty = [round(float(i),2) for i in data]
    #print(empty)
    plt.figure(figsize=(10, 8), dpi=80)
    plt.subplot(111)
    plt.plot(date, data, color="blue", linewidth=2.5, linestyle="-")
    # plt.ylim((0, 10))
    plt.ylabel("Price")
    plt.title("Price Difference")
    plt.show()

    adftest = adfuller(data)
    result = pd.Series(adftest[0:4], index = ["Test Statistic", "p-value", "Lags Used", "Number of Observations Used"])
    for key, value in adftest[4].items():
        result["Critical Value (%s)" % key] = value
    print(result)

    mean = np.mean(data)
    print(mean)
    std = np.std(data)
    print(std)
    up = mean +  std
    down = mean -  std
    time = data.index
    mean_line = pd.Series(mean, index = time)
    up_line = pd.Series(up, index = time)
    down_line = pd.Series(down, index = time)
    set = pd.concat([data, mean_line, up_line, down_line], axis = 1)
    set.columns = ["spreadprice", "mean", "upper", "down"]
    #print(set)
    set.plot()
    plt.show()


    return mean, std

def TRADE(stock1, stock2, mean, std, tradestartdate, tradeenddate):
    Benchmark = "000001.SZ"
    Money = 1000000
    Stock = 0
    Adjust = 5
    Inimoney = 1000000

    data1, data2 = GETSQL(stock1, stock2, tradestartdate, tradeenddate)
    date = data1["trade_date"]
    data = data1["close"] - data2["close"]
    #print(data)

    up = mean + std
    down = mean - std
    flag = 0
    for i in range(len(data)):
        if(data[i] > up and flag==0):
            flag = 1
            roundblocks = Money // (100 * data2["close"][i])
            Stock = Stock + roundblocks * 100
            Money = Money - roundblocks * 100 * data2["close"][i]
            if(roundblocks > 0):
                print("买入 %d 股 %s" % (roundblocks * 100, stock2))
                print("%s : 持仓 %d 股 %s 余额 %d " % (date[i], Stock, stock2, Money))
                print("******************************")
        elif(data[i] < down and flag==0):
            flag = -1
            roundblocks = Money // (100 * data1["close"][i])
            Stock = Stock + roundblocks * 100
            Money = Money - roundblocks * 100 * data1["close"][i]
            if (roundblocks > 0):
                print("买入 %d 股 %s" % (roundblocks * 100, stock1))
                print("%s : 持仓 %d 股 %s 余额 %d " % (date[i], Stock, stock1, Money))
                print("******************************")
        elif(flag==1 and data[i] < mean):
            flag = 0
            Money = Money + Stock * data2["close"][i]
            if (Stock > 0):
                print("卖出 %d 股 %s" % (Stock, stock2))
                print("%s : 持仓 0 股  余额 %d " % (date[i], Money))
                print("******************************")
            Stock = 0
        elif(flag==-1 and data[i] > mean):
            flag = 0
            Money = Money + Stock * data1["close"][i]
            if(Stock > 0):
                print("卖出 %d 股 %s" % (Stock, stock1))
                print("%s : 持仓 0 股  余额 %d " % (date[i], Money))
                print("******************************")
            Stock = 0


    if (Stock > 0 and flag == 1):
        Money = Money + Stock * data2["close"][i]
        print("卖出 %d 股 %s" % (Stock, stock2))
        print("%s : 持仓 0 股 %s 余额 %d " % (date[i], stock2, Money))
        print("******************************")
    if (Stock > 0 and flag == -1):
        Money = Money + Stock * data1["close"][i]
        print("卖出 %d 股 %s" % (Stock, stock1))
        print("%s : 持仓 0 股 %s 余额 %d " % (date[i], stock1, Money))
        print("******************************")
    print("账户余额：%s" % Money)
    return

def main():
    # stock1 = "600642.SH"
    # stock2 = "600863.SH"
    stock1 = "600033.SH"
    stock2 = "601117.SH"
    startdate = "2015-08-01"
    enddate = "2016-12-01"
    tradestartdate = "2016-12-01"
    tradeenddate = "2017-11-01"
    data1, data2 = GETSQL(stock1, stock2, startdate, enddate)
    CHART(stock1, stock2, data1, data2)
    mean, std = STRATEGY(stock1, stock2, data1, data2)
    TRADE(stock1, stock2, mean, std, tradestartdate, tradeenddate)
    return


if __name__=="__main__":
    main()