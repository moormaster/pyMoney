- [x] remove "category changesign" command from commandline parser
- [x] rename "category list" command to "category tree", "category listnames" to "category list"
- [x] allow to mention parent category names to make duplicate category names unique 

      Category  Shortest unique name
      
      All       All
       Costs    Costs
         Misc   Costs.Misc
       Incoming Incoming
         Misc   Incoming.Misc
         
      $ ./pyMoney.py transaction add Misc 25.00
      ERROR
      $ ./pyMoney.py transaction add Costs.Misc 25.00
      OK
- [x] refactor category add/rename/move - replace find_first_node() with find_first_node_by_relative_pathname()  
- [x] transactions should always happen between a source and a target category
      this enables one to keep track of the amount of money stored within each bank
      account:
      
      All
       Internal     External.In.Wages   -> Giro.In              1500.00
        Cash        Giro.Out            -> External.Out.Misc      25.00 DVD
         In         Giro.Out            -> Bar.In                400.00 EC Machine
         Out        Cash.Out            -> External.Out.Life      70.00 Food
        Giro    
         In
         Out
       External
        In
         Wages
        Out
         Life
         Misc
      
      $ ./pyMoney.py summary categories
      
      node                                         amount        sum
      
      All                                            0.00       0.00
       Internal                                      0.00    1405.00
        Bar                                          0.00     330.00
         In                                        400.00     400.00
         Out                                       -70.00     -70.00
        Giro                                         0.00    1075.00
         In                                       1500.00    1500.00
         Out                                      -425.00    -425.00
       External                                      0.00   -1405.00  
        In                                           0.00   -1500.00
         Wages                                   -1500.00   -1500.00
        Out                                          0.00      95.00
         Life                                       70.00      70.00
         Misc                                       25.00      25.00

- [x] allow date filter from or until
    $ ./pyMoney.py transaction list ">=2010" 01
    -- print all transactions beginning from 2010 01
    
    $ ./pyMoney.py summary categories "<=2010" 02
    -- print category sums of all transactions until 2010 02 --