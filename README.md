# pyMoney
A commandline tool to track personal expenses within a tree of categories

## Example usage:
```
$ ./pyMoney.py category list
+ All


$ ./pyMoney.py category add All + Incoming
$ ./pyMoney.py category add All - Outgoing
$ ./pyMoney.py category add Outgoing + Life
$ ./pyMoney.py category add Outgoing + Misc

$ ./pyMoney.py category list
+ All
        - Outgoing
                + Misc
                + Life
        + Incoming


$ ./pyMoney.py transaction add 2016-01-01 Incoming 1500 "Wages"
$ ./pyMoney.py transaction add 2016-01-05 Life 30 "Food"
$ ./pyMoney.py transaction add 2016-01-10 Misc 14.99 "Favorite DVD"

$ ./pyMoney.py summary categories 2016 01
node                                         amount        sum

 + All                                         0.00    1455.01
     - Outgoing                                0.00     -44.99
         + Life                               30.00     -30.00
         + Misc                               14.99     -14.99
     + Incoming                             1500.00    1500.00

$ ./pyMoney.py transaction list 2016 01
     Index Date       Category                 Amount Comment
         0 2016-01-01 Incoming                1500.00 Wages
         1 2016-01-05 Life                     -30.00 Food
         2 2016-01-10 Misc                     -14.99 Favorite DVD
```
