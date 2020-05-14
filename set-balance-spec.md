Balances Module Specifications
==============================

```k
requires "set-balance.k"

module VERIFICATION
    imports SET-BALANCE

    syntax Action ::= totalBalance ( AccountId )
 // --------------------------------------------
    rule <k> totalBalance(AID) => total_balance(AID) ... </k>

    syntax Bool ::= nonDustBalances ( Int , AccountsCell ) [function, functional]
    rule nonDustBalances (_, _) => true [owise]
    rule nonDustBalances ( EXISTENTIAL_DEPOSIT
                         , <accounts>
                             <account>
                               ...
                               <freeBalance> FREE_BALANCE </freeBalance>
                               <reservedBalance> RESERVED_BALANCE </reservedBalance>
                               ...
                             </account>
                             ...
                           </accounts>
                         )
      => false
      requires FREE_BALANCE <Int EXISTENTIAL_DEPOSIT
        orBool RESERVED_BALANCE <Int EXISTENTIAL_DEPOSIT

   syntax Int ::= freeBalance ( AccountId , AccountsCell ) [function, functional]
   rule freeBalance(WHO, <accounts> <account> <accountID> WHO </accountID> <freeBalance> FB </freeBalance> ... </account> ... </accounts>) => FB
   rule freeBalance(_, _) => 0 [owise]

   syntax Bool ::= balanceOK ( Int , Int ) [function, functional]
   rule balanceOK(I, ED) => I ==Int 0 orBool I >=Int ED

   syntax KItem ::= checkBalance( AccountId )
   rule <k> checkBalance( WHO ) => . ... </k>
        <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>

     requires balanceOK( free_balance( WHO ),     EXISTENTIAL_DEPOSIT )
      andBool balanceOK( reserved_balance( WHO ), EXISTENTIAL_DEPOSIT )


endmodule

module SET-BALANCE-SPEC
    imports VERIFICATION
```

### `total_balance` tests

```
    rule <k> totalBalance(AID) => B +Int A </k>
         <account>
           <accountID> AID </accountID>
           <freeBalance> A </freeBalance>
           <reservedBalance> B </reservedBalance>
           ...
         </account>
```

### No Zero-Balance Accounts Exist

```
    rule <k> set_balance(Root, WHO, FREE_BALANCE, RESERVED_BALANCE) => . ... </k>
         <now> _ => ?_ </now>
         <events> _ => ?_ </events>
         <return-value> _ => ?_ </return-value>
         <call-stack> _ => ?_ </call-stack>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <creationFee> _ </creationFee>
         <transferFee> _ </transferFee>
         <totalIssuance> TOTAL_ISSUANCE => ?TOTAL_ISSUANCE </totalIssuance>
         <accounts> ACCOUNTS => ?ACCOUNTS' </accounts>
      requires nonDustBalances(EXISTENTIAL_DEPOSIT, <accounts> ACCOUNTS </accounts>)
       andBool nonDustBalances(EXISTENTIAL_DEPOSIT, <accounts> ?ACCOUNTS' </accounts>)
       andBool #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE -Int freeBalance(WHO, <accounts> ACCOUNTS </accounts>)))
```

This property shows that `set_balance` will not result in a zero-balance attack.
**TODO**: Generalize to any EntryAction.
**TODO**: Assertions about log events.

```k
    rule <k> set_balance(Root, WHO, FREE_BALANCE', RESERVED_BALANCE') ~> checkBalance( WHO ) => . ... </k>
         <totalIssuance> TOTAL_ISSUANCE => TOTAL_ISSUANCE +Int ( FREE_BALANCE' -Int free_balance(WHO) ) +Int ( RESERVED_BALANCE' -Int reserved_balance(WHO) ) </totalIssuance>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>

      requires #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int free_balance( WHO )))
       andBool #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int free_balance( WHO )) +Int (RESERVED_BALANCE' -Int reserved_balance( WHO )))
       andBool ( (balanceOK(free_balance( WHO ), EXISTENTIAL_DEPOSIT) andBool balanceOK(reserved_balance( WHO ), EXISTENTIAL_DEPOSIT))
     impliesBool (balanceOK(FREE_BALANCE', EXISTENTIAL_DEPOSIT) andBool balanceOK(RESERVED_BALANCE', EXISTENTIAL_DEPOSIT))
               )
       andBool ( FREE_BALANCE'     >=Int EXISTENTIAL_DEPOSIT )
       andBool ( RESERVED_BALANCE' >=Int EXISTENTIAL_DEPOSIT )
```

```
    rule <k> set_balance_reserved ( WHO , RESERVED_BALANCE' ) => . </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <totalIssuance> TOTAL_ISSUANCE +Int ( FREE_BALANCE' -Int FREE_BALANCE ) => TOTAL_ISSUANCE +Int ( FREE_BALANCE' -Int FREE_BALANCE ) +Int ( RESERVED_BALANCE' -Int RESERVED_BALANCE ) </totalIssuance>
         <account>
           <accountID> WHO </accountID>
           <freeBalance> FREE_BALANCE' </freeBalance>
           <reservedBalance> RESERVED_BALANCE => RESERVED_BALANCE' </reservedBalance>
           ...
         </account>
      requires #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE) +Int (RESERVED_BALANCE' -Int RESERVED_BALANCE))
       andBool EXISTENTIAL_DEPOSIT <=Int RESERVED_BALANCE'
```

```k
endmodule
```
