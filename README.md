# pyMoney
A commandline tool to track personal expenses within a tree of categories

## Example usage:
```
$ ./pyMoney.py category tree
All

# set up accounts
$ ./pyMoney.py category add All Expenses
$ ./pyMoney.py category add Expenses Misc
$ ./pyMoney.py category add Expenses GoingOut
$ ./pyMoney.py category add Expenses DailyLife
$ ./pyMoney.py category add All Assets
$ ./pyMoney.py category add Assets Bank
$ ./pyMoney.py category add Assets Cash
$ ./pyMoney.py category add All Income
$ ./pyMoney.py category add Income Wages
$ ./pyMoney.py category add All Liabilities
$ ./pyMoney.py category add Liabilities VISA
$ ./pyMoney.py category add All Equity
$ ./pyMoney.py category add Equity OpeningBalance

# print the category tree
$ ./pyMoney.py category tree
All
  Expenses
    Misc
    GoingOut
    DailyLife
  Assets
    Bank
    Cash
  Income
    Wages
  Liabilities
    VISA
  Equity
    OpeningBalance

# set up initial balance for assets and liabilities
$ ./pyMoney.py transaction add 2015-12-31 OpeningBalance Bank 2000.00
$ ./pyMoney.py transaction add 2015-12-31 OpeningBalance Cash 120.00
$ ./pyMoney.py transaction add 2015-12-31 VISA OpeningBalance 34.40

# sum up all transations to show current asset and liability balance
$ ./pyMoney.py summary categories --category Assets
node      amount   sum + sum -     sum

  Assets    0.00 2120.00  0.00 2120.00
    Bank 2000.00 2000.00  0.00 2000.00
    Cash  120.00  120.00  0.00  120.00
$ ./pyMoney.py summary categories --category Liabilities
node          amount sum +  sum -    sum

  Liabilities   0.00  0.00 -34.40 -34.40
    VISA      -34.40  0.00 -34.40 -34.40

# add some transactions
$ ./pyMoney.py transaction add 2016-01-01 Wages Bank 1500 "Wages"
$ ./pyMoney.py transaction add 2016-01-01 Bank Cash 100 "EC Money"
$ ./pyMoney.py transaction add 2016-01-03 Bank VISA 34.40 "Pay credit card debts"
$ ./pyMoney.py transaction add 2016-01-05 Cash DailyLife 30 "Food"
$ ./pyMoney.py transaction add 2016-01-10 Bank Misc 14.99 "Favorite DVD"
$ ./pyMoney.py transaction add 2016-01-10 VISA GoingOut 45.00 "Visiting concert of favorite band"

# for each category list the sum of transactions that happened during january 2016
$ ./pyMoney.py summary categories 2016 01
node            amount   sum +    sum -      sum

All               0.00 1724.39 -1724.39     0.00
  Expenses        0.00   89.99     0.00    89.99
    Misc         14.99   14.99     0.00    14.99
    GoingOut     45.00   45.00     0.00    45.00
    DailyLife    30.00   30.00     0.00    30.00
  Assets          0.00 1600.00  -179.39  1420.61
    Bank       1350.61 1500.00  -149.39  1350.61
    Cash         70.00  100.00   -30.00    70.00
  Income          0.00    0.00 -1500.00 -1500.00
    Wages     -1500.00    0.00 -1500.00 -1500.00
  Liabilities     0.00   34.40   -45.00   -10.60
    VISA        -10.60   34.40   -45.00   -10.60

# list all transactions from january 2016
$ ./pyMoney.py transaction list 2016 01
Index       Date FromCategory ToCategory  Amount Comment

    3 2016-01-01 Wages        Bank       1500.00 Wages
    4 2016-01-01 Bank         Cash        100.00 EC Money
    5 2016-01-03 Bank         VISA         34.40 Pay credit card debts
    6 2016-01-05 Cash         DailyLife    30.00 Food
    7 2016-01-10 Bank         Misc         14.99 Favorite DVD
    8 2016-01-10 VISA         GoingOut     45.00 Visiting concert of favorite band

# list all transactions that affected the Cash account from january 2016
$ ./pyMoney.py transaction list 2016 01 --category Cash
Index       Date FromCategory ToCategory Amount Comment

    4 2016-01-01 Bank         Cash       100.00 EC Money
    6 2016-01-05 Cash         DailyLife   30.00 Food
                                          
                              + Cash     100.00 
                              - Cash     -30.00 
                              sum Cash    70.00 

# sum up all transactions to show all asset and liability balances
$ ./pyMoney.py summary categories --category Assets
node      amount   sum +   sum -     sum

  Assets    0.00 3720.00 -179.39 3540.61
    Bank 3350.61 3500.00 -149.39 3350.61
    Cash  190.00  220.00  -30.00  190.00
$ ./pyMoney.py summary categories --category Liabilities
node          amount sum +  sum -    sum

  Liabilities   0.00 34.40 -79.40 -45.00
    VISA      -45.00 34.40 -79.40 -45.00
```
