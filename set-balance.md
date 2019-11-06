`set_balance` spec
==================

State Model
-----------

```k
module SET-BALANCE-SPEC
    imports INT
    imports LIST
    imports SET

    configuration
      <set-balance>
        <k> $ACTION:Action </k>
        <events> .List </events>
        <root-accounts> .Set </root-accounts>
        <existentialDeposit> 0 </existentialDeposit>
        <totalIssuance> 0 </totalIssuance>
        <accounts>
          <account multiplicity="*" type="Map">
            <accountID> .AccountId:AccountId </accountID>
            <freeBalance> 0 </freeBalance>
            <reservedBalance> 0 </reservedBalance>
            <nonce> .Nonce </nonce>
          </account>
        </accounts>
      </set-balance>
```

Data
----

-   An `AccountId` is an optional `Int`.
-   A `Nonce` is an optional `Int`.
-   An `Event` records some happenning.

```k
    syntax AccountId ::= ".AccountId" | Int
 // ---------------------------------------

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

    syntax Actions ::= List{Action, ""}
 // -----------------------------------
    rule <k> A:Action AS:Actions => A ~> AS ... </k>
```

### `set_free_balance`

-   Updates an accounts balance if the new balance is above the existential threshold.
-   Kills the account if the balance goes below the existential threshold and the reserved balance is non-zero.
-   Reaps the account if the balance goes below the existential threshold and the reserved balance is zero.

```k
    syntax Action ::= "set_free_balance" "(" AccountId "," Int ")"
 // --------------------------------------------------------------
    rule [free-account-updated]:
         <k> set_free_balance(WHO, BALANCE) => Updated ... </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <freeBalance> _ => BALANCE </freeBalance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [free-account-killed]:
         <k> set_free_balance(WHO, BALANCE) => AccountKilled ... </k>
         <events> ... (.List => ListItem(DustEvent(FREE_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <nonce> _ => .Nonce </nonce>
           <freeBalance> FREE_BALANCE => 0 </freeBalance>
           <reservedBalance> RESERVED_BALANCE </reservedBalance>
           ...
         </account>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
       andBool 0 <Int RESERVED_BALANCE

    rule [free-account-reaped]:
         <k> set_free_balance(WHO, BALANCE) => AccountKilled ... </k>
         <events> ... (.List => ListItem(DustEvent(FREE_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <accounts>
           ( <account>
               <accountID> WHO </accountID>
               <freeBalance> FREE_BALANCE </freeBalance>
               <reservedBalance> 0 </reservedBalance>
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
 // ------------------------------------------------------------------
    rule [reserved-account-updated]:
         <k> set_reserved_balance(WHO, BALANCE) => Updated ... </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <reservedBalance> _ => BALANCE </reservedBalance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [reserved-account-killed]:
         <k> set_reserved_balance(WHO, BALANCE) => AccountKilled ... </k>
         <events> ... (.List => ListItem(DustEvent(RESERVED_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <nonce> _ => .Nonce </nonce>
           <freeBalance> FREE_BALANCE  </freeBalance>
           <reservedBalance> RESERVED_BALANCE => 0 </reservedBalance>
           ...
         </account>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
       andBool 0 <Int FREE_BALANCE

    rule [reserved-account-reaped]:
         <k> set_reserved_balance(WHO, BALANCE) => AccountKilled ... </k>
         <events> ... (.List => ListItem(DustEvent(RESERVED_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <accounts>
           ( <account>
               <accountID> WHO </accountID>
               <freeBalance> 0 </freeBalance>
               <reservedBalance> RESERVED_BALANCE </reservedBalance>
               ...
             </account>
          => .Bag
           )
           ...
         </accounts>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
```

### `set_balance`

* Sets the new free balance
* Creates suitible imbalances (both positive and negative).
* Calls `set_free_balance` with the new free balance.
* Calls `set_reserved_balance` with the new reserved balance.
* **FIXME**: these semantics **do not** include lookup of an `AccountId` from a `Source`.

```k
    syntax Action ::= "set_balance" "(" AccountId "," AccountId "," Int "," Int ")"
 // -------------------------------------------------------------------------------
    rule [balance-set]:
        <k> set_balance(ORIGIN, WHO, FREE_BALANCE, RESERVED_BALANCE) => set_balance_free(WHO, FREE_BALANCE) set_balance_reserved(WHO, RESERVED_BALANCE) ... </k>
        <root-accounts> ROOTS </root-accounts>
      requires ORIGIN in ROOTS
```

### `set_balance_free`

* Sets the new free balance
* Emits an imbalance event
* Helper function for `set_balance`
* **FIXME** use saturating arithmetic

```k
    syntax Action ::= "set_balance_free" "(" AccountId "," Int ")"
    syntax Action ::= "set_balance_reserved" "(" AccountId "," Int ")"
 // ------------------------------------------------------------------
    rule [balance-set-free]:
         <k> set_balance_free(WHO, FREE_BALANCE) => set_free_balance(WHO, FREE_BALANCE) ... </k>
         <totalIssuance> BALANCE => BALANCE +Int FREE_BALANCE </totalIssuance>
         <account>
           <accountID> WHO </accountID>
           ...
         </account>

    rule [balance-set-reserved]:
         <k> set_balance_reserved(WHO, RESERVED_BALANCE) => set_reserved_balance(WHO, RESERVED_BALANCE) ... </k>
         <totalIssuance> BALANCE => BALANCE +Int RESERVED_BALANCE </totalIssuance>
         <account>
           <accountID> WHO </accountID>
           ...
         </account>
```

```k
endmodule
```
