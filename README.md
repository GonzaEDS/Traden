#Traden
#### Video Demo: https://youtu.be/1fbS-lAvrOo
#### Description:

Traden is a cryptocurrency trading simulation platform in which users can become familiar with buying and selling cryptocurrencies or practice their trading skills without compromising their capital.
The platform builds on the same base idea as CS50 Finance, but based on cryptocurrencies rather than stocks. To do this, it obtains the information in real time from the CoinMaretCap API, and also uses charts offered by TradingView.
For the layout I used a Bootstrap template. After the home page, the first page that we can visit is the Dashboard. Users can access this page without registering or logging in (but they must do so in order to make purchases and have a wallet).

##### Dashboard

The Dashboard contains a list of cryptocurrencies with their respective logo, symbol, name and price. The information comes from CoinMarketCap.
By clicking on any logo we can access a page whose url is dynamically generated. In it you can see the name of the chosen cryptocurrency. A chart that indicates in real time the price of that currency in dollars. A brief description of the coin and a series of related links. All the information comes from the CoinMarketCap API, except for the chart which is a TradingView widget.

Having checked the information of different cryptocurrencies we can make the decision to buy to start building our Wallet. For this we need to register by entering a username and password.


##### Buy Sell

Once registered and logged in, we can access the page to buy and sell. In it there is a form and some extra information that is displayed dynamically in relation to the input.

To begin with, we choose with a radio button if we want to buy and sell.

If we want to buy, we can choose options with a drop-down button with the currencies that we already have in our wallet among the payment options. Whereas if we want to sell, the drop-down will be on the side where the currency we sell is selected.

Once we have selected a currency that we want to buy, and the amount that we want to buy, we can see on the other side the amount that it will cost in dollars. And if we select another currency as a payment method, we will also see the equivalent in dollars below.


##### Wallett

If we have sufficient funds, we choose an existing currency to buy and select a different currency as a means of payment, the operation will be carried out successfully and we will be automatically redirected to our Wallet where we can see a table that indicates the currencies we have, the dollars we have and a total dollar equivalent of everything in it.

We can also access the Wallet at any time while we are logged in by going to the username in the navigation bar, and then to Wallet within the drop-down menu

##### History

Another option that we see in the drop-down menu is the history. When we go to the history we see a record of all our purchases and sales, the price we pay or receive for them in the currency in which we pay or receive it, and the precise date and time that we carry out the operation. For clarity, purchases are shown in green and sales in red.


##### My Account

Finally we have the My Account section in the drop-down menu, in it we can choose to change our username or password and we also have the option to increase the funds available in dollars.

### Project files


#### Apidata.py

contains the function that makes the call to the CoinMarketCap API. It saves the information of two calls to two different endpoints in two external files Data.txt and Info.txt, so that it can be checked by the developer at any time; and then reorders it in a dictionary which is useful for application purposes. It also reads and updates the now.txt file with the minute the information was updated so that it is updated every time it is required only if one minute has elapsed.

#### App.py

it is the main flask file. It contains the functions for each of the pages that the web contains and uses the dictionary created in Apidata.py to send the necessary information to the templates.

#### Traden.db

It is the sqlite3 file in which all the information required for the users is stored. It contains three tables. The table called users stores the username, the password hash and the available cash as well as an id that is the primary key.

The table called wallets uses the id as a foreign key. It contains a column called symbol that will hold the currency symbol. A column called name for your name, a column called coins that will save the amount. This table is used to create the table in the Wallet template, where the user can see their currencies.

The table named History also uses Id as a foreign key and contains the tables, symbol, coins, price, and transacted, which stads for the date and time. This table is used to show the table with the transaction history to the user.

### Static and templates

The static folder contains all the images and the main CSS of the project

The templates folder contains all the HTMl templates that receive the information from App.py to generate the web