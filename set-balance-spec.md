Balances Module Specifications
==============================

```k
requires "set-balance.k"

module VERIFICATION
    imports SET-BALANCE

    syntax Action ::= totalBalance ( AccountId )
 // --------------------------------------------
    rule <k> totalBalance(AID) => total_balance(AID) ... </k>
endmodule

module SET-BALANCE-SPEC
    imports VERIFICATION
```

### `total_balance` tests

```k
    rule <k> totalBalance(AID) => 50 </k>
         <account>
           <accountID> AID </accountID>
           <freeBalance> 30 </freeBalance>
           <reservedBalance> 20 </reservedBalance>
           ...
         </account>
```

```k
endmodule
```
