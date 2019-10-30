`set_balance` spec
==================

State Model
-----------

```k
module SET-BALANCE-SPEC
    imports INT
    imports LIST

    configuration
      <set-balance>
        <k> $ACTION:Action </k>
        <events> .List </events>
        <existentialDeposit> 0 </existentialDeposit>
        <accounts>
          <account multiplicity="*" type="Map">
            <accountID> .AccountId:AccountId </accountID>
            <balance> 0 | 0 </balance>
            <nonce> .Nonce </nonce>
          </account>
        </accounts>
      </set-balance>
```

Data
----

-   An `AccountId` is an optional `Int`.
-   A `Balance` is a tuple of `Int` (for free/reserved balance).
-   A `Nonce` is an optional `Int`.
-   An `Event` records some happenning.

```k
    syntax AccountId ::= ".AccountId" | Int
 // ---------------------------------------

    syntax Balance ::= Int "|" Int
 // ------------------------------

    syntax Nonce ::= ".Nonce" | Int
 // -------------------------------

    syntax Event ::= DustEvent ( Int )
 // ----------------------------------
```

Results
-------

A `Result` is the return value of an execution step.

-   `AccountKilled` indicates that the free balance goes below the existential threshold.
-   `Updated` indicates that an account was updated successfully.

```k
    syntax Result ::= "AccountKilled" | "Updated"
 // ---------------------------------------------
```

Actions and Results
-------------------

An `Action` is an execution step (or the result of an execution step).
A `Result` is considered an `Action`.

```k
    syntax Action ::= Result
 // ------------------------
```

### `set_free_balance`

-   Updates an accounts balance if the new balance is above the existential threshold.
-   Kills the account if the balance goes below the existential threshold and the reserved balance is non-zero.
-   Reaps the account if the balance goes below the existential threshold and the reserved balance is zero.

```k
    syntax Action ::= "set_free_balance" "(" AccountId "," Int ")"
 // --------------------------------------------------------------
    rule [account-updated]:
         <k> set_free_balance(WHO, BALANCE) => Updated </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <balance> (_ => BALANCE) | _ </balance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [account-killed]:
         <k> set_free_balance(WHO, BALANCE) => AccountKilled </k>
         <events> ... (.List => ListItem(DustEvent(FREE_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <nonce> _ => .Nonce </nonce>
           <balance> (FREE_BALANCE => 0) | RESERVED_BALANCE </balance>
           ...
         </account>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
       andBool 0 <Int RESERVED_BALANCE

    rule [account-reaped]:
         <k> set_free_balance(WHO, BALANCE) => AccountKilled </k>
         <events> ... (.List => ListItem(DustEvent(FREE_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <accounts>
           ( <account>
               <accountID> WHO </accountID>
               <balance> FREE_BALANCE | 0 </balance>
               ...
             </account>
          => .Bag
           )
           ...
         </accounts>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
```

### `set_reserved_balance`

-   Updates an accounts balance if the new balance is above the existential threshold.
-   Kills the account if the balance goes below the existential threshold and the free balance is non-zero.
-   Reaps the account if the balance goes below the existential threshold and the free balance is zero.

```k
    syntax Action ::= "set_reserved_balance" "(" AccountId "," Int ")"
 // --------------------------------------------------------------
    rule [reserved-account-updated]:
         <k> set_reserved_balance(WHO, BALANCE) => Updated </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <balance> _ | (_ => BALANCE) </balance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [reserved-account-killed]:
         <k> set_reserved_balance(WHO, BALANCE) => AccountKilled </k>
         <events> ... (.List => ListItem(DustEvent(RESERVED_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <nonce> _ => .Nonce </nonce>
           <balance> FREE_BALANCE | (RESERVED_BALANCE => 0) </balance>
           ...
         </account>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
       andBool 0 <Int FREE_BALANCE

    rule [reserved-account-reaped]:
         <k> set_reserved_balance(WHO, BALANCE) => AccountKilled </k>
         <events> ... (.List => ListItem(DustEvent(RESERVED_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <accounts>
           ( <account>
               <accountID> WHO </accountID>
               <balance> 0 | RESERVED_BALANCE </balance>
               ...
             </account>
          => .Bag
           )
           ...
         </accounts>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
```

```k
endmodule
```
