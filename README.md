# pyMoney
A commandline tool to track personal expenses within a tree of categories

## Example usage:
```
$ ./pyMoney.py category tree
All
$ ./pyMoney.py category add All Accounts
$ ./pyMoney.py category add Accounts Bank
$ ./pyMoney.py category add Accounts Cash
$ ./pyMoney.py category add All External
$ ./pyMoney.py category add External Misc
$ ./pyMoney.py category add External Life
$ ./pyMoney.py category add External Wages

$ ./pyMoney.py category tree
All
  Accounts
    Bank
    Cash
  External
    Misc
    Life
    Wages

$ ./pyMoney.py transaction add 2016-01-01 Wages Bank 1500 "Wages"
$ ./pyMoney.py transaction add 2016-01-01 Bank Cash 100 "EC Money"
$ ./pyMoney.py transaction add 2016-01-05 Cash Life 30 "Food"
$ ./pyMoney.py transaction add 2016-01-10 Bank Misc 14.99 "Favorite DVD"

$ ./pyMoney.py summary categories 2016 01
node         amount   sum +    sum -      sum

All            0.00 1644.99 -1644.99     0.00
  Accounts     0.00 1600.00  -144.99  1455.01
    Bank    1385.01 1500.00  -114.99  1385.01
    Cash      70.00  100.00   -30.00    70.00
  External     0.00   44.99 -1500.00 -1455.01
    Misc      14.99   14.99     0.00    14.99
    Life      30.00   30.00     0.00    30.00
    Wages  -1500.00    0.00 -1500.00 -1500.00

$ ./pyMoney.py transaction list 2016 01
Index       Date FromCategory ToCategory  Amount Comment

    0 2016-01-01 Wages        Bank       1500.00 Wages
    1 2016-01-01 Bank         Cash        100.00 EC Money
    2 2016-01-05 Cash         Life         30.00 Food
    3 2016-01-10 Bank         Misc         14.99 Favorite DVD

$ ./pyMoney.py transaction list 2016 01 --category Cash
Index       Date FromCategory ToCategory Amount Comment

    1 2016-01-01 Bank         Cash       100.00 EC Money
    2 2016-01-05 Cash         Life        30.00 Food
                                          
                              + Cash     100.00 
                              - Cash     -30.00 
                              sum Cash    70.00 

$ ./pyMoney.py summary categories --category Accounts
node        amount   sum +   sum -     sum

  Accounts    0.00 1600.00 -144.99 1455.01
    Bank   1385.01 1500.00 -114.99 1385.01
    Cash     70.00  100.00  -30.00   70.00
```
