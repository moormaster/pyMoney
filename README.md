# pyMoney
A commandline tool to track personal expenses within a tree of categories

## Example usage:
```
$ ./pyMoney.py category tree
All

$ ./pyMoney.py category add All Accounts
$ ./pyMoney.py category add Accounts Bank
$ ./pyMoney.py category add Accounts Cash
$ ./pyMoney.py category add Bank In
$ ./pyMoney.py category add Bank Out
$ ./pyMoney.py category add Cash In
$ ./pyMoney.py category add Cash Out
$ ./pyMoney.py category add All External
$ ./pyMoney.py category add External In
$ ./pyMoney.py category add External Out
$ ./pyMoney.py category add External.In Misc
$ ./pyMoney.py category add External.In Life
$ ./pyMoney.py category add External.Out Wages


$ ./pyMoney.py category tree
All
        Accounts
                Bank
                        In
                        Out
                Cash
                        In
                        Out
        External
                In
                        Misc
                        Life
                Out
                        Wages


$ ./pyMoney.py transaction add 2016-01-01 Wages Bank.In 1500 "Wages"
$ ./pyMoney.py transaction add 2016-01-01 Bank.Out Cash.In 100 "EC Money"
$ ./pyMoney.py transaction add 2016-01-05 Cash.Out Life 30 "Food"
$ ./pyMoney.py transaction add 2016-01-10 Bank.Out Misc 14.99 "Favorite DVD"


$ ./pyMoney.py summary categories 2016 01
node                                                        amount        sum

All                                                           0.00       0.00
    Accounts                                                  0.00    1455.01
        Bank                                                  0.00    1385.01
            In                                             1500.00    1500.00
            Out                                            -114.99    -114.99
        Cash                                                  0.00      70.00
            In                                              100.00     100.00
            Out                                             -30.00     -30.00
    External                                                  0.00   -1455.01
        In                                                    0.00      44.99
            Misc                                             14.99      14.99
            Life                                             30.00      30.00
        Out                                                   0.00   -1500.00
            Wages                                         -1500.00   -1500.00


$ ./pyMoney.py transaction list 2016 01
     Index Date       FromCategory         ToCategory                                   Amount Comment             
         0 2016-01-01 Wages                Bank.In                                     1500.00 Wages               
         1 2016-01-01 Bank.Out             Cash.In                                      100.00 EC Money            
         2 2016-01-05 Cash.Out             Life                                          30.00 Food                
         3 2016-01-10 Bank.Out             Misc                                          14.99 Favorite DVD        
```
