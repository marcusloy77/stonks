<h1> Stock Webscraper Project </h1>

A basic stock webscraper that takes stocks included in the 'Shares_List.xlsx' file and computes their data into the 'Shares.xlsx' file by scraping the relevant data (price, movement etc) from au.finance.yahoo.com

I utilized threading technology to speed the process up, and smtplib to set up an email system that emails me alerts whenever a stock I'm holding goes either up or down by 5%.

I utilized pandas for the scraping technology to allow the HTML file to be parsed more easily.