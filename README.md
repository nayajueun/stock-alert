# stock-alert
Alert users by SMS any dramatic change in stocks of their interest by requesting API on a regular interval.
Appropriate for users in CET time zone.

## Features
- Receives a name of the company of their interest and a phone number from users.
- Runs three times during the opening hour of the stock market and sends an alert by SMS, if the change in the stock price for two hours was greater than 4%.
- Additionally runs every morning in the weekdays and sends an alert by SMS, if the change in the stock price for two hours was greater than 4%.
- Each alert message contains three popular headlines of real-time news data. Formatted as below.

![alt text](https://github.com/nayajueun/stock-alert/blob/master/demo.jpg?raw=true)

## Dependencies
- Stock API provider: "https://www.alphavantage.co/"
- News API provider: "https://newsapi.org/"

## Install
Packages to install:
- pandas
- requests
- schedule
- twilio
Run `pip install {package to install}` and run the project!
