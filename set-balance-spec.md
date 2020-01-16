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

```
    rule <k> totalBalance(AID) => 50 </k>
         <account>
           <accountID> AID </accountID>
           <freeBalance> 30 </freeBalance>
           <reservedBalance> 20 </reservedBalance>
           ...
         </account>
```

### No Zero-Balance Accounts Exist

This property shows that `set_balance` will not result in a zero-balance attack.
**TODO**: Generalize to any EntryAction.
**TODO**: Assertions about log events.

```k
    rule <k> set_balance(Root, WHO, FREE_BALANCE', RESERVED_BALANCE') => . ... </k>
         <events> _ => _ </events>
         <totalIssuance> TOTAL_ISSUANCE </totalIssuance>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <freeBalance> FREE_BALANCE => FREE_BALANCE' </freeBalance>
           <reservedBalance> RESERVED_BALANCE => RESERVED_BALANCE' </reservedBalance>
           ...
         </account>
      requires #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE))
       andBool #inWidth(96, (TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE)) +Int (RESERVED_BALANCE' -Int RESERVED_BALANCE))
       andBool EXISTENTIAL_DEPOSIT <=Int FREE_BALANCE'
       andBool EXISTENTIAL_DEPOSIT <=Int RESERVED_BALANCE'
```

```k
endmodule
```
