import requests
from datetime import datetime
import csv
import pandas as pd

# from IO String
try:
    from io import StringIo
except ImportError:
    from io import StringIO


class BitcoinAveragePrice:
    def __init__(self):
        self.dataframe = None

    def load_prices(self):
        URL_API = "https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?"
        params = {
            'range': '2y',
            'interval': '1d',
            'events': 'history',
            'includeAdjustedClose': 'true',
        }
        time_series = {}
        response = requests.get(URL_API, params=params)
        file = StringIO(response.text)
        reader = csv.reader(file)
        data = list(reader)
        for row in data[1:]:
            date = row[0]

            closing_price = row[4]
            if closing_price == 'null':
                pass
            else:
                time_series[datetime.strptime(date, '%Y-%m-%d').date()] = float(closing_price)
        data_to_load = {"Date": time_series.keys(),
                        "Price": time_series.values()}
        dataframe = pd.DataFrame(data_to_load)
        self.dataframe = dataframe.iloc[::-1]
        return self.dataframe


def moving_average(dataframe, days_for_moving_average):
    global days
    days = days_for_moving_average
    price_list = dataframe['Price'].to_list()
    print(price_list)
    moving_average_list = []
    price_sum = 0
    number = 0
    while number < days_for_moving_average:
        for price in price_list:
            price_sum += price
            number += 1

            if number == days_for_moving_average:
                break
        average = price_sum / days_for_moving_average
        moving_average_list.append(average)
        price_list = price_list[1:]
        price_sum = 0
        number = 0
        if len(moving_average_list) == (len(dataframe['Price'].to_list()) + 1 - days_for_moving_average):
            break
    moving_average_dict = {}
    date_list = dataframe["Date"].to_list()
    updated_date_list = date_list[:-(days_for_moving_average - 1):]

    moving_average_dataframe = pd.DataFrame({"Date": updated_date_list, "Price": moving_average_list})
    return moving_average_dataframe

#
# def return_moving_average_days(moving_average_dict, start_date, number_of_days):
#     specific_moving_average = {}
#     start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
#     datetimelist = sorted(moving_average_dict.keys(), key=lambda x: x, reverse=True)
#     key_dates = []
#     for date in datetimelist:
#         if (start_datetime - date).days >= 0:
#             key_dates.append(date)
#         if len(key_dates) == number_of_days:
#             break
#     last_days_dict = {}
#     for date in key_dates:
#         last_days_dict[date] = moving_average_dict[date]
#
#     print(last_days_dict)
#     return last_days_dict

    # sort keys in desc order


#     new_date_time_list = []
#     print(datetimelist)
#     moving_average_list = [u for u in moving_average_dict.values()]
#     for i in datetimelist:
#         if (start_datetime - i).days >= 0:
#             new_date_time_list.append(i)
#     new_date_time_list2 = new_date_time_list[new_date_time_list.index(start_datetime)-number_of_days:]
#     print(new_date_time_list2)
#     for i in new_date_time_list2:
#         specific_moving_average[i] = moving_average_dict[i]
#     return(specific_moving_average)
#
#
#  {
#     '2020-04-20': 40000,
#      '2020-04-21': 40001
# }
def buy_or_sell(price_time_series, day_ma, date_time_object):
    updated_date_list = []
    buy_or_sell_list = []

    reversed_price_time_series = price_time_series.iloc[::-1]
    # january_prices = reversed_price_time_series[290:320]
    # print(january_prices)
    # print('*************Reversed Price Time Series*********************')
    # print(reversed_price_time_series)
    #date_time_object = datetime.strptime('2020-01-01', '%Y-%m-%d').date()

    # print("**************************Reversed Moving Average")
    reversed_ma = day_ma.iloc[::-1]
    # january_ma = reversed_ma[286:]

    # print(january_ma)

    important_date_list = []
    index_list = []
    # print(reversed_price_time_series)
    # print(reversed_ma)
    buy_sell_signal_list = []
    for index in range(0, len(reversed_price_time_series["Price"].to_list())):

        if date_time_object <= reversed_price_time_series.iloc[index]['Date']:
            index_list.append(index)
            important_date_list.append(reversed_price_time_series.iloc[index]['Date'])
            if reversed_price_time_series.iloc[index][1] > reversed_ma.iloc[index - days][1]:
                buy_or_sell_list.append("B")
                data_tuple = (reversed_price_time_series.iloc[index]['Date'], 'B', reversed_price_time_series.iloc[index][1], 0)
            elif reversed_price_time_series.iloc[index][1] < reversed_ma.iloc[index - days][1]:
                buy_or_sell_list.append("S")
                data_tuple = (reversed_price_time_series.iloc[index]['Date'], 'S', reversed_price_time_series.iloc[index][1], 0)
            buy_sell_signal_list.append(data_tuple)


    # for index in index_list:
    #     if reversed_price_time_series.iloc[index][1] > reversed_ma.iloc[index-days][1]:
    #         buy_or_sell_list.append("B")
    #     elif reversed_price_time_series.iloc[index][1] < reversed_ma.iloc[index-days][1]:
    #         buy_or_sell_list.append("S")
        # print(reversed_ma.iloc[index-days][0])
    # print("*****************************")



    print(important_date_list)
    # print(len(buy_or_sell_list))
    # print(len(reversed_price_time_series["Price"].to_list()))
    buy_or_sell_dataframe = pd.DataFrame(buy_sell_signal_list, columns=["Date", "Buy/Sell", "Price", "MarketValue"])
    print(buy_or_sell_dataframe)
    start_portfolio_value = 500000
    current_portfolio_cash = start_portfolio_value
    portfolio_wealth = [start_portfolio_value]
    buy_count = 0
    bitcoins_purchased = 0
    for row in buy_or_sell_dataframe.iterrows():
    # for index in range(0, len(important_date_list)):
        data = row[1]
        current_price = data['Price']
        signal = data['Buy/Sell']
        if signal == 'B':
            if current_portfolio_cash > 0:
                bitcoins_purchased += float(current_portfolio_cash / data['Price'])
                current_portfolio_cash = 0
        else:# S
            current_portfolio_cash += bitcoins_purchased * current_price
            bitcoins_purchased = 0
        data['MarketValue'] = bitcoins_purchased * current_price
        # if buy_count == 0:
        #     data = row[1]
        #     if data['Buy/Sell'] == 'B':
        #         bitcoins_purchased = float(money/data['Price'])
        #         # print(bitcoins_purchased)
        #         buy_count += 1
        # elif buy_count != 0:
        #     if data['Buy/Sell'] == 'B':
        #         pass
        #     elif data['Buy/Sell'] == "S":
        #         wealth = bitcoins_purchased * data['Price']
        #         portfolio_wealth.append(wealth)
        #         money = wealth
        #         buy_count = 0
    # print(reversed_price_time_series.iloc[:30])

    print(portfolio_wealth)



# def buy_or_sell(five_day_ma, two_hundred_day_ma):
#     updated_date_list = []
#     buy_or_sell_list = []
#     for date1, date2 in zip(five_day_ma["Date"].to_list(), two_hundred_day_ma["Date"].to_list()):
#         if date1 == date2:
#             updated_date_list.append(date1)
#     print(updated_date_list)
#     for index in range(0, len(updated_date_list)):
#         if five_day_ma.iloc[index][1] > two_hundred_day_ma.iloc[index][1]:
#             buy_or_sell_list.append("B")
#         elif five_day_ma.iloc[index][1] < two_hundred_day_ma.iloc[index][1]:
#             buy_or_sell_list.append("S")
#     buy_or_sell_dataframe = pd.DataFrame({
#         "Date": updated_date_list,
#         "B/S": buy_or_sell_list
#     })
#     print(buy_or_sell_dataframe)
#     return buy_or_sell_dataframe


if __name__ == '__main__':
    bitCoinPriceAverage = BitcoinAveragePrice()
    loaded_prices = bitCoinPriceAverage.load_prices()

    two_hundred_day_ma = moving_average(loaded_prices, 200)
    buy_or_sell(loaded_prices, two_hundred_day_ma, datetime.strptime('2020-01-01', '%Y-%m-%d').date())





