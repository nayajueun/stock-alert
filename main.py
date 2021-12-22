import pandas
import requests
import schedule
import time
from twilio.rest import Client
from datetime import date

companies_data = pandas.read_csv("nasdaq_screener_1639426793803.csv")
COMPANY = None
STOCK = None
name_input = None

stock_api_key = open("stock_api_key.txt", "r").read()
news_api_key = open("news_api_key.txt", "r").read()
account_sid = open("account_sid.txt", "r").read()
auth_token = open("auth_token.txt", "r").read()
client = Client(account_sid, auth_token)
today = date.today()

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# --------------SEARCH FOR THE COMPANY-----------------#

found = False
while not found:
    name_input = input("Which company's stock price would you like to receive alerts on?\n"
                       "(Please type the full name of the company. e.g. 'International Business Machines' instead of "
                       "IBM) ").capitalize()
    input_length = len(name_input)
    symbol_list = list(companies_data["Symbol"])
    name_list = list(companies_data["Name"])

    row = 0
    interested_index = []
    which_index = None
    for name in list(companies_data["Name"]):
        if name[:input_length] == name_input:
            interested_index.append(row)
        row += 1

    if len(interested_index) == 0:
        print(f"Cannot find a company named '{name_input}'. Please try again. ")
    else:
        if len(interested_index) == 1:
            which_index = interested_index[0]
        if len(interested_index) > 1:
            print("We've got a multiple result. ")
            number = 1
            for i in interested_index:
                print(f"{number}. {name_list[i]}")
                number += 1

            ans_nb = int(input("Please type the number of the company you would like to receive an alert. "))
            which_index = interested_index[ans_nb - 1]

        COMPANY = name_list[which_index]
        answer = input(f"Would you like to receive an alert for {COMPANY}? "
                       f"Please type Yes or No.").capitalize()

        if answer == "Yes":
            found = True
            STOCK = symbol_list[which_index]

phone_number = input("Please insert your phone number including country code. (in the format of +123456789012) ")

# -----------NEWS MESSAGE GENERATOR----------------#

def generate_news():
    """Returns a string of live news."""

    news_parameters = {
        "q": name_input,
        "from": today,
        "sortBy": "popularity",
        "apiKey": news_api_key
    }
    news = ""
    response = requests.get(NEWS_ENDPOINT, params=news_parameters)
    response.raise_for_status()
    news_data = response.json()
    try:
        for n in range(3):
            news_dict = news_data["articles"][n]
            news += f"\nHeadline: {news_dict['title']}\nBrief: {news_dict['description']}\n{news_dict['url']}\n"
    except KeyError:
        news = "No relevant news found"
    finally: return news


# ----------MORNING ALERT-------------#

def send_message_morning():
    """Send SMS to user."""
    stock_parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "outputsize": "compact",
        "apikey": stock_api_key
    }

    r = requests.get(STOCK_ENDPOINT, stock_parameters)
    stock_data = r.json()["Time Series (Daily)"]
    data_list = [value for (key, value) in stock_data.items()]
    ytd_closing_price = float(data_list[0]["4. close"])
    dbytd_closing_price = float(data_list[1]["4. close"])

    if abs(ytd_closing_price - dbytd_closing_price) > dbytd_closing_price * 0.04:
        percentage_change = ytd_closing_price / dbytd_closing_price - 1
        if percentage_change > 0:
            text = f"{STOCK} 🔺{int(abs(percentage_change) * 100)}%"
        else:
            text = f"{STOCK} 🔻{int(abs(percentage_change) * 100)}%"
        text += " overall in a day" + generate_news()

        print(text)

        message = client.messages \
            .create(
            body=text,
            from_='+14752502580',
            to=phone_number
        )
        print(message.status)


schedule.every().monday.at("9:30").do(send_message_morning())  # in CET
schedule.every().tuesday.at("9:30").do(send_message_morning())
schedule.every().wednesday.at("9:30").do(send_message_morning())
schedule.every().thursday.at("9:30").do(send_message_morning())
schedule.every().friday.at("9:30").do(send_message_morning())


# ---------------DAYTIME ALERT---------------------#

def send_message_alert():
    """Send SMS to user."""
    stock_parameters_ = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": STOCK,
        "interval": "60min",
        "apikey": stock_api_key
    }

    r_ = requests.get(STOCK_ENDPOINT, stock_parameters_)
    stock_data_ = r_.json()["Time Series (60min)"]
    data_list_ = [value for (key, value) in stock_data_.items()]
    cur_price = float(data_list_[0]["1. open"])
    prev_price = float(data_list_[2]["1. open"])

    if abs(cur_price - prev_price) > prev_price * 0.04:
        percentage_change_ = cur_price / prev_price - 1
        if percentage_change_ > 0:
            text_ = f"{STOCK} 🔺{int(abs(percentage_change_) * 100)}%"
        else:
            text_ = f"{STOCK} 🔻{int(abs(percentage_change_) * 100)}%"
        text_ += " overall in two hours" + generate_news()

        print(text_)

        message = client.messages \
            .create(
            body=text_,
            from_='+14752502580',
            to=phone_number
        )
        print(message.status)


schedule.every().monday.at("17:30").do(send_message_alert())  # in CET
schedule.every().monday.at("19:30").do(send_message_alert())
schedule.every().monday.at("21:30").do(send_message_alert())
schedule.every().tuesday.at("17:30").do(send_message_alert())
schedule.every().tuesday.at("19:30").do(send_message_alert())
schedule.every().tuesday.at("21:30").do(send_message_alert())
schedule.every().wednesday.at("17:30").do(send_message_alert())
schedule.every().wednesday.at("19:30").do(send_message_alert())
schedule.every().wednesday.at("21:30").do(send_message_alert())
schedule.every().thursday.at("17:30").do(send_message_alert())
schedule.every().thursday.at("19:30").do(send_message_alert())
schedule.every().thursday.at("21:30").do(send_message_alert())
schedule.every().friday.at("17:30").do(send_message_alert())
schedule.every().friday.at("19:30").do(send_message_alert())
schedule.every().friday.at("21:30").do(send_message_alert())

while True:
    schedule.run_pending()
    time.sleep(1)
