Balances Module Specifications
==============================

```k
requires "set-balance.k"

module VERIFICATION
    imports SET-BALANCE

    syntax Action ::= totalBalance ( AccountId )
 // --------------------------------------------
    rule <k> totalBalance(AID) => total_balance(AID) ... </k>

    syntax Bool ::= nonDustBalances ( Set ) [function, functional]
    rule nonDustBalances(_) => false [owise]
    rule nonDustBalances(.Set) => true
    rule [[ nonDustBalances((SetItem(WHO) => .Set) REST) ]]
        <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
        <account>
          <accountID> WHO </accountID>
          <freeBalance> FREE_BALANCE </freeBalance>
          <reservedBalance> RESERVED_BALANCE </reservedBalance>
          ...
        </account>
     requires EXISTENTIAL_DEPOSIT <=Int FREE_BALANCE
      andBool EXISTENTIAL_DEPOSIT <=Int RESERVED_BALANCE
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

```k
    rule <k> set_balance(_, _, _, _) => . ... </k>
         <now> _ => ?_ </now>
         <events> _ => ?_ </events>
         <return-value> _ => ?_ </return-value>
         <call-stack> _ => ?_ </call-stack>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <creationFee> _ </creationFee>
         <transferFee> _ </transferFee>
         <totalIssuance> _ => ?_ </totalIssuance>
         <accountSet> ACCOUNT_SET => ?ACCOUNT_SET' </accountSet>
         <accounts> ACCOUNTS => ?ACCOUNTS' </accounts>
      requires // accountsValid(ACCOUNT_SET, ACCOUNTS)
       // andBool accountsValid(?ACCOUNT_SET', ?ACCOUNTS')
               nonDustBalances(ACCOUNT_SET)
       andBool nonDustBalances(?ACCOUNT_SET')
```

This property shows that `set_balance` will not result in a zero-balance attack.
**TODO**: Generalize to any EntryAction.
**TODO**: Assertions about log events.

```
    rule <k> set_balance(Root, WHO, FREE_BALANCE', RESERVED_BALANCE') => . ... </k>
         <totalIssuance> TOTAL_ISSUANCE => TOTAL_ISSUANCE +Int ( FREE_BALANCE' -Int FREE_BALANCE ) +Int ( RESERVED_BALANCE' -Int RESERVED_BALANCE ) </totalIssuance>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <freeBalance> FREE_BALANCE => FREE_BALANCE' </freeBalance>
           <reservedBalance> RESERVED_BALANCE => RESERVED_BALANCE' </reservedBalance>
           ...
         </account>
      requires #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE))
       andBool #inWidth(96, TOTAL_ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE) +Int (RESERVED_BALANCE' -Int RESERVED_BALANCE))
       andBool EXISTENTIAL_DEPOSIT <=Int FREE_BALANCE'
       andBool EXISTENTIAL_DEPOSIT <=Int RESERVED_BALANCE'
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
