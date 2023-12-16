# Importing required libraries 
import requests
import json
import time
import os.path
from datetime import datetime   


# if the path exist adds the new values
def addPricesInExistingFiles(ticker, rqst_dict, key):
    file = open('final_project/data/'+ticker + ".csv")
    lines = file.readlines()
    
    while len(lines[-1]) == 1:           
        lines.pop()
    
    last_line = lines[-1]
    items = last_line.split(",")
    last_date =items[0]
    
    #getting the last date to of csv file to compare
    last_date = datetime.strptime(last_date, '%Y-%m-%d')                    
   
    price = []                                                              
    for date in rqst_dict[key[0]]:

        row = ""
        row += date + ","
        row += rqst_dict[key[0]][date][key[1]] + ","
        row +=  rqst_dict[key[0]][date][key[4]] + ","
        row += rqst_dict[key[0]][date][key[2]] + ","
        row += rqst_dict[key[0]][date][key[3]] + "\n"
        #comparing date with last date to avoid over wrinting in .csv file 
        if datetime.strptime(date, '%Y-%m-%d') > last_date:                                                
            price.append(row)                                         
        
    #reversing the price to get latest data at the end for convenience 
    price.reverse()                                                         
    
    #appending data to .csv file
    csv_file = open('final_project/data/'+ticker + ".csv", "a")             
    
    
    for row in price:
        csv_file.write(row)
    
    csv_file.close
    
    return ;
        

# if the path not exists
def createNewfile(ticker, rqst_dict, key):
       
    price = []
    for date in rqst_dict[key[0]]:

        row = ""
        row += date + ","
        row += rqst_dict[key[0]][date][key[1]] + ","
        row +=  rqst_dict[key[0]][date][key[4]] + ","
        row += rqst_dict[key[0]][date][key[2]] + ","
        row += rqst_dict[key[0]][date][key[3]] + "\n"
        
        price.append(row)
        
    price.reverse()
    
    
    csv_file = open('final_project/data/'+ticker + ".csv", "w")
    csv_file.write("date"+ "," + "open"+ "," + "close" + "," + "high" + "," + "low" + "\n") 
    
    for row in price:
        csv_file.write(row)
    
    csv_file.close
    return ;

#creating  function for download/update the price list 
def updatedata(ticker):                                                         
    
    
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+ticker+'&outputsize=full&apikey=NG9C9EPVYBMQT0C8'
    # requesting data from the alphavantage url
    request = requests.get(url)                                                 
    #storing the result in a json file as string
    rqst_dict = json.loads(request.text)                                        
    key = []
    #creating keys to loop through the json
    key.append("Time Series (Daily)")                                          
 
    key.append("1. open")
    key.append("2. high")
    key.append("3. low")
    key.append("4. close")
    
    #creating .csv files as per the ticker name
    filename = 'final_project/data/'+ticker + ".csv"                            
    
    #checking ticker_name.csv file exist or not
    if os.path.exists(filename):                                                
                                            
        addPricesInExistingFiles(ticker, rqst_dict, key)
        
    else:
        
        createNewfile(ticker, rqst_dict, key)
    return ;
    
        
  
#creating function to get data from .csv files    
def getdata(ticker):                                                            
    
    
    prices = [float(line.split(",")[2]) for line in open('final_project/data/'+ticker + ".csv").readlines()[1:] if len(line) > 1]
    
    return prices
    
# function for calculating average
def avg(lst):
    return sum(lst)/len(lst)
#function for mean reversion strategy    
def meanReversionStrategy(prices):                                              
    print('Mean Reversion Strategy')
    print('-------------------------------------------')
    print()
    #setting the initial valus
    i = 0                                                                       
    buy = 0
    short = 0
    total_profit = 0
    for p in prices:
        if i >= 5: 
            moving_average = avg(prices[i-5:i])
            buy_price = moving_average * .98
            sell_price = moving_average * 1.02
            #simple moving average logic, not mean
            #Checking buying conditions
            if p < buy_price and buy == 0:                           
               
                buy = p
                
                if short != 0 and buy != 0:
                    total_profit += short - buy
                    
                short = 0
                if i == len(prices)-1:
                    print("buy this the stock today")
            #sell (same as short)
            elif p > sell_price and short == 0:                      
                short = p
                
                if short != 0 and buy != 0:
                    total_profit += short - buy
                    
                buy = 0
                if i == len(prices)-1:
                    print("sell/short this the stock today")
        i += 1
    print()
    #Calculating final percentage based on first buying price
    final_percentage = (total_profit / prices[0]) * 100
    
    
    return total_profit, final_percentage


#function for simple moving average strategy
def movingavg(prices):                                                          
    print('Simple Moving Average Strategy')
    print('-------------------------------------')
    print()
    
    #Setting initials conditions                                                
    prior_price = []                                                            
    bought = False                                                              
    buyprice = -9999                                                            
    firstprice = -9999
    total_profit = 0
    for i in range(0,len(prices)):                                
        price = prices[i]
        if len(prior_price) < 5:                              
            prior_price.append(price)                                           
            continue
        #buying condition   
        elif (price > avg(prior_price[-5:-1])) and not bought:                    
            bought = True
           
            if firstprice == -9999:
                firstprice = price
            buyprice = price
            
            if i == len(prices) - 1:
                print("Buy this stock today")
        #Checking selling condition
        elif avg(prior_price[-5:-1]) > price and bought:                           
            bought = False
           
            total_profit += (price - buyprice)                                  
            if i == len(prices) - 1:
                print("sell this stock today")                          
        #updating prior_price list with new price
        prior_price.append(price)                                
       
    #calculating the return 
    avgreturn = round((total_profit/firstprice)*100, 2)                         
    print()
    
    return total_profit, avgreturn
    


# function for simple moving average crossover
def smaCrossoverTenFifty(prices):
    print('SMA crossover Strategy')
    print('---------------------------------')
    print()
    
                                               
    prior_price = []                                                            
    bought = False                                                              
    #setting the initial value
    buyprice = -1                                                               
    firstprice = -1
    total_profit = 0
    for i in range(0,len(prices)):                                
        price = prices[i] 
        if len(prior_price) < 50:                              
            prior_price.append(price)                                           
            continue
        tenDayAvg = avg(prior_price[-10:-1])
        fiftyDayAvg = avg(prior_price[-50:-1])
        #buying condition
        if tenDayAvg > fiftyDayAvg and not bought:           
            bought = True
           
            if firstprice == -1:
                firstprice = price
            buyprice = price
            if i == len(prices) - 1:
                print("Buy this stock today") 
        #selling condition
        elif fiftyDayAvg > tenDayAvg and bought:                  
            bought = False
           
                                                                                
            total_profit += (price - buyprice)
            if i == len(prices) - 1:
                print("sell this stock today")                                  
        #updating prior_price list with new price
        prior_price.append(price)                               
       
    #calculating anual return
    anu_return = round((total_profit/firstprice)*100, 2)                         
    print()
    
    return total_profit, anu_return
    
#function to save the result in a json file    
def saveResults(result):                                                        
    
    json.dump(result, open("final_project/data/results.json", "w")) 
    
#creating the ticker list
tickers = ['AAPL', 'GIL']#,'AMZN','TXN','META','XRX','GOOG','MSFT','LIN','TSLA']   

#creating an empty dictionary for storing results
result = {}                                                                     
max_return_strategy = {}
max_return_stock = {}
for ticker in tickers:
    #exception handling
    try:                                                                        
        print(ticker)
        updatedata(ticker)
        
        prices = getdata(ticker)
        
        profit_mr, anu_return_mr = meanReversionStrategy(prices)
        
        result[ticker + '-profit_mr'] = profit_mr
        result[ticker + '-precentage_mr'] = anu_return_mr
        max_return_strategy[ticker + '_mr'] = anu_return_mr
        
        profit_sma, anu_return_sma = movingavg(prices)
        result[ticker + '-profit_sma'] = profit_sma
        result[ticker + '-precentage_sma'] = anu_return_sma
        max_return_strategy[ticker + '_sma'] = anu_return_sma
        
        profit_smac, anu_return_smac = smaCrossoverTenFifty(prices)
        result[ticker + '-profit_smac'] = profit_smac
        result[ticker + '-precentage_smac'] = anu_return_smac
        max_return_strategy[ticker + '_smac'] = anu_return_smac
        
        max_value_strategy = max(max_return_strategy, key=max_return_strategy.get)
        #print(max_value_strategy)
        max_return_stock[max_value_strategy] = max_return_strategy[max_value_strategy]
        max_return_strategy.clear()

        
    except:
        print('Error happened while data processing')
    #putting 12 sec delay between every ticker request 
    time.sleep(12)                                                                
    
#Logic for identify which stock and strategy made the most profit
max_stock_strategy = max(max_return_stock, key = max_return_stock.get)
max_stock_strategy_value = max_return_stock[max_stock_strategy]
print('Maximum return: ', max_stock_strategy,' of ', max_stock_strategy_value,'%')
saveResults(result)

input('Hit Enter')