import requests
from bs4 import BeautifulSoup
import json, csv
import pandas as pd
from tqdm import tqdm
import time
from multiprocessing.pool import ThreadPool as Pool
import config
import smtplib


#Basic Webscraping Function
def getData(symbol):
    url = f'https://au.finance.yahoo.com/quote/{symbol}'
    headers = {'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    stock = {'stock' : symbol,
	'price' : soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('span')[0].text,
    'change' : soup.find('div', {'class':'D(ib) Mend(20px)'}).find_all('span')[1].text,}
    return stock

# Parsing stock numbers from strings
def extractChange(stock):
    x = stock.split(" ")   
    y = round((float(x[5][1:-2])),3)
    return y
    
#Email Function
def stockMail(subject, msg):
    try:
        server=smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail(config.RECIEVING_ADDRESS, config.RECIEVING_ADDRESS, message)
        server.quit()
        print("Email Sent")
    except:
        print("Email Failed")

#Excel Setup
path = 'Shares_List.xlsx'
df1 = pd.read_excel(path, dtype="string",index_col=0)
df2 = df1["Share"]
ShareIt = len(df2)
print(ShareIt)

pool_size = (df2.shape[0])

# Threaded Stock Webscraping
def worker(x):
	df3 = df2[x:x+1].to_string()
	t = str.split(df3)[1]
	stock = getData(t)
	df1["Last Price"][x:x+1] = stock["price"]
	df1["Today Change"][x:x+1] = stock["change"]
	# print(stock)
	return df1

pool = Pool(pool_size)

for x in range(df2.shape[0]):
	pool.apply_async(worker, (x,))
pool.close()
pool.join()



# Email loop to let you know if stocks have changed dramatically
for x in range(df2.shape[0]):

    sChange = df1["Today Change"][x:x+1].to_string()
    stockChangePercentFloat = extractChange(sChange)
    stockNameBig = df1["Share"][x:x+1].to_string()
    stockNameLittle = stockNameBig[5:]
    if (stockChangePercentFloat < -5):
        stockMail(stockNameLittle + " drop " + str(stockChangePercentFloat), "null")
    if (stockChangePercentFloat > 5):
        stockMail(str(stockNameLittle) + " gain " + str(stockChangePercentFloat), "null")
        print("Email sent")



#Extra Column Declarations
dfCost = df1["Ave. Cost"]
dfLast = df1["Last Price"]
dfUnits = df1["Units"]
PortTotal = 0

avePercentGain = 0
TotalGainPort = 0
TotalCostPort = 0
TotalWorthBig = 0

#Extra Collumn Calcs
for x in range(df2.shape[0]):
    dfUnits2 = dfUnits[x:x+1].to_string()
    dfCost2 = dfCost[x:x+1].to_string()
    dfLast2 = dfLast[x:x+1].to_string()
    Units = float(str.split(dfUnits2)[1])
    if (Units == 0.0):
        df1["Ave. Cost"][x:x+1] = df1["Last Price"][x:x+1]
        dfCost2 = df1["Last Price"][x:x+1].to_string()
    Cost = float(str.split(dfCost2)[1])
    try:
        Last = float(str.split(dfLast2)[1])
    except:
        print("string failed")
        print(df1["Share"][x:x+1])
        Last = 1.0
	
	

    percentGain = round(((Last/Cost) - 1),3)
    TotalGain = round (((Units*Last) - (Units*Cost)),3)
    TotalCost = round((Units*Cost),3)
    TotalWorth = round((Units*Last),3)
    PortTotal = round((PortTotal + TotalWorth),3)
    
    avePercentGain = avePercentGain + percentGain
    TotalGainPort = TotalGain + TotalGainPort
    TotalCostPort = TotalCost + TotalCostPort
    TotalWorthBig = TotalWorth + TotalWorthBig
    
	
    df1["Percent Gain"][x:x+1] = str(percentGain)
    df1["Total Gain"][x:x+1] = str(TotalGain)
    df1["Total Cost"][x:x+1] = str(TotalCost)
    df1["Total Worth"][x:x+1] = str(TotalWorth)


dfWorth = df1["Total Worth"]

#Folio Percentage Calc
for x in range(df2.shape[0]):
	worth = dfWorth[x:x+1].to_string()
	worth2 = float(str.split(worth)[1])
	PortWorth = round((worth2/PortTotal),3)
	df1["Portfolio Percentage"][x:x+1] = str(PortWorth)


df1["Percent Gain"][ShareIt] = avePercentGain
df1["Total Gain"][ShareIt] = TotalGainPort
df1["Total Cost"][ShareIt] = TotalCostPort
df1["Total Worth"][ShareIt] = TotalWorthBig

print("Average Percentage Gain Today = " + str(round((avePercentGain),2)))
print ("Total Cost = " + str(round(TotalCostPort)))
print("Total Portfolio Worth = " + str(round(TotalWorthBig)))
print ("Total Money Made = " + str(round(TotalGainPort)))




with pd.ExcelWriter(r"C:\Users\marcu\OneDrive\Desktop\Coding Projects\Python\Shares\Shares.xlsx") as writer:
	df1.to_excel(writer)

print("done")

#To Add:
#Loading Bar
#Total Vals
#Native Support - Autorun



