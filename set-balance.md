`set_balance` spec
==================

State Model
-----------

```k
module SET-BALANCE-SPEC
    imports INT
    imports DOMAINS
    imports COLLECTIONS

    configuration
      <set-balance>
        <k> $ACTION:Action </k>
        <now> 0 </now>
        <events> .List </events>
        <return-value> .Result </return-value>
        <call-stack> .List </call-stack>
        <existentialDeposit> 0 </existentialDeposit>
        <creationFee> 0 </creationFee>
        <transferFee> 0 </transferFee>
        <totalIssuance> 0 </totalIssuance>
        <accounts>
          <account multiplicity="*" type="Map">
            <accountID> .AccountId:AccountId </accountID>
            <freeBalance> 0 </freeBalance>
            <reservedBalance> 0 </reservedBalance>
            <vestingBalance> 0 </vestingBalance>
            <nonce> .Nonce </nonce>
            <locks> .Set </locks>
          </account>
        </accounts>
      </set-balance>
```

Data
----

- An `AccountId` is an `Int`.
- An `Origin` is an `AccountId`, `Root`, or `None`.
- A `Nonce` is an optional `Int`.
- An `Event` records some happenning.

```k
    syntax AccountId ::= ".AccountId" | Int
 // ---------------------------------------

    syntax Origin ::= AccountId | ".Root" | ".None"
 // -----------------------------------------------

    syntax Nonce ::= ".Nonce" | Int
 // -------------------------------

    syntax Event ::= DustEvent ( Int )
 // ----------------------------------
```

Some predicates which help specifying behavior:

-   `#inWidth`: Specify that a given number is in some bitwidth.

```k
    syntax Bool ::= #inWidth(Int, Int) [function, functional]
 // ---------------------------------------------------------
    rule #inWidth(N, M) => 0 <=Int M andBool M <Int (2 ^Int N)
```

Results
-------

A `Result` is the return value of an execution step.

-   `AccountKilled` indicates that the free balance goes below the existential threshold.
-   `Updated` indicates that an account was updated successfully.

```k
    syntax Result ::= ".Result" | "AccountKilled" | "Updated"
 // ---------------------------------------------------------
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
    rule [free-account-updated]:
         <k> set_free_balance(WHO, BALANCE) => . ... </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <freeBalance> _ => BALANCE </freeBalance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [free-account-killed]:
         <k> set_free_balance(WHO, BALANCE) => . ... </k>
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
         <k> set_free_balance(WHO, BALANCE) => . ... </k>
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
         <k> set_reserved_balance(WHO, BALANCE) => . ... </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <accountID> WHO </accountID>
           <reservedBalance> _ => BALANCE </reservedBalance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [reserved-account-killed]:
         <k> set_reserved_balance(WHO, BALANCE) => . ... </k>
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
         <k> set_reserved_balance(WHO, BALANCE) => . ... </k>
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

```k
    syntax Action ::= "set_balance" "(" AccountId "," AccountId "," Int "," Int ")"
 // -------------------------------------------------------------------------------
    rule [balance-set]:
        <k> set_balance(Root, WHO, FREE_BALANCE, RESERVED_BALANCE)
         => set_balance_free(WHO, FREE_BALANCE)
         ~> set_balance_reserved(WHO, RESERVED_BALANCE)
        ...
        </k>
```

Helpers for calling `set_free_balance` and `set_reserved_balance`.

* Sets the new free balance
* Emits an imbalance event
* Helper function for `set_balance`

```k
    syntax Action ::= "set_balance_free"     "(" AccountId "," Int ")"
    syntax Action ::= "set_balance_reserved" "(" AccountId "," Int ")"
 // ------------------------------------------------------------------
    rule [balance-set-free]:
         <k> set_balance_free(WHO, FREE_BALANCE') => set_free_balance(WHO, FREE_BALANCE') ... </k>
         <totalIssuance> ISSUANCE => ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE) </totalIssuance>
         <account>
           <accountID> WHO </accountID>
           <freeBalance> FREE_BALANCE </freeBalance>
           ...
         </account>
      requires #inWidth(64, ISSUANCE +Int (FREE_BALANCE' -Int FREE_BALANCE))

    rule [balance-set-reserved]:
         <k> set_balance_reserved(WHO, RESERVED_BALANCE') => set_reserved_balance(WHO, RESERVED_BALANCE') ... </k>
         <totalIssuance> ISSUANCE => ISSUANCE +Int (RESERVED_BALANCE' -Int RESERVED_BALANCE) </totalIssuance>
         <account>
           <accountID> WHO </accountID>
           <reservedBalance> RESERVED_BALANCE </reservedBalance>
           ...
         </account>
      requires #inWidth(64, ISSUANCE +Int (RESERVED_BALANCE' -Int RESERVED_BALANCE))
```

### `transfer`

Transfer some liquid free balance to another account.

`transfer` will set the `FreeBalance` of the sender and receiver.
It will decrease the total issuance of the system by the `TransferFee`.
If the sender's account is below the existential deposit as a result
of the transfer, the account will be reaped.

The dispatch origin for this call must be `Signed` by the transactor.

```k
    syntax ExitenceRequirement ::= ".AllowDeath"
                                 | ".KeepAlive"

    syntax Action ::= transfer(AccountId, AccountId, Int)
 // ---------------------------------------------------------------------
    rule [transfer-self]:
         <k> transfer(ORIGIN, ORIGIN, _) => . ... </k>

    rule [transfer-existing-account]:
         <k> transfer(ORIGIN, DESTINATION, AMOUNT)
          => set_free_balance(ORIGIN, SOURCE_BALANCE -Int AMOUNT -Int FEE)
          ~> set_free_balance(DESTINATION, DESTINATION_BALANCE +Int AMOUNT)
         ...
         </k>
         <totalIssuance> ISSUANCE => ISSUANCE -Int FEE </totalIssuance>
         <transferFee> FEE </transferFee>
         <accounts>
           <account>
             <accountID> ORIGIN </accountID>
             <freeBalance> SOURCE_BALANCE </freeBalance>
             ...
           </account>
           <account>
             <accountID> DESTINATION </accountID>
             <freeBalance> DESTINATION_BALANCE </freeBalance>
             ...
           </account>
         </accounts>
      requires ORIGIN =/=K DESTINATION
       andBool DESTINATION_BALANCE >Int 0
       andBool SOURCE_BALANCE >=Int (AMOUNT +Int FEE)
       andBool ensure_can_withdraw(ORIGIN, Transfer, SOURCE_BALANCE -Int AMOUNT -Int FEE)

    rule [transfer-create-account]:
         <k> transfer(ORIGIN, DESTINATION, AMOUNT)
          => set_free_balance(ORIGIN, SOURCE_BALANCE -Int AMOUNT -Int CREATION_FEE)
          ~> set_free_balance(DESTINATION, AMOUNT)
         ...
         </k>
         <totalIssuance> ISSUANCE => ISSUANCE -Int CREATION_FEE </totalIssuance>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <creationFee> CREATION_FEE </creationFee>
         <accounts>
           <account>
             <accountID> ORIGIN </accountID>
             <freeBalance> SOURCE_BALANCE </freeBalance>
             ...
           </account>
           <account>
             <accountID> DESTINATION </accountID>
             <freeBalance> 0 </freeBalance>
             <reservedBalance> 0 </reservedBalance>
             ...
           </account>
         </accounts>
      requires ORIGIN =/=K DESTINATION
       andBool SOURCE_BALANCE >=Int (AMOUNT +Int CREATION_FEE)
       andBool EXISTENTIAL_DEPOSIT <=Int AMOUNT
       andBool ensure_can_withdraw(ORIGIN, Transfer, SOURCE_BALANCE -Int AMOUNT -Int CREATION_FEE)
```

Force a transfer from any account to any other account.  This can only be done by root.

```k
    syntax Action ::= "force_transfer" "(" Origin "," AccountId "," AccountId "," Int ")"
 // ----------------------------------------------------------------------------------------
    rule [force-transfer]:
         <k> force_transfer(.Root, SOURCE, DESTINATION, AMOUNT) => transfer(SOURCE, DESTINATION, AMOUNT) ... </k>
```

Call Frames
===========

Function call and return.

```k
    syntax CallFrame ::= frame(continuation: K)
    syntax Action ::= call   ( Action )
                    | return ( Result )
 // -----------------------------------
    rule [call]:
         <k> call(Action) ~> CONT => Action </k>
         <call-stack> .List => ListItem(frame(CONT)) ... </call-stack>

    rule [return]:
         <k> return(R) ~> _ => CONT </k>
         <return-value> _ => R </return-value>
         <call-stack> ListItem(frame(CONT)) => .List ... </call-stack>

    rule [return-unit]:
         <k> . => CONT </k>
         <return-value> _ => .Result </return-value>
         <call-stack> ListItem(frame(CONT)) => .List ... </call-stack>
```

Ensure that a given amount can be withdrawn from an account.

**FIXME** actually implement this ― this is currently a stub that always returns `?True`

```k
    syntax WithdrawReason ::= "TransactionPayment"
                            | "Transfer"
                            | "Reserve"
                            | "Fee"
                            | "Tip"
 // -------------------------------

    syntax Bool ::= "ensure_can_withdraw" "(" AccountId "," WithdrawReason "," Int ")" [function, functional]
 // ---------------------------------------------------------------------------------------------------------
    rule ensure_can_withdraw(_, _, _) => true [owise]

    rule [[ ensure_can_withdraw(WHO, Transfer #Or Reserve, BALANCE) => false ]]
         <account>
           <accountID> WHO </accountID>
           <vestingBalance> VESTING_BALANCE </vestingBalance>
           ...
         </account>
      requires VESTING_BALANCE <Int BALANCE

    rule [[ ensure_can_withdraw(WHO, REASON, BALANCE) => false ]]
         <now> NOW </now>
         <account>
           <accountID> WHO </accountID>
           <locks> ACCOUNT_LOCKS </locks>
           ...
         </account>
      requires activeLocks(ACCOUNT_LOCKS, NOW, REASON, BALANCE)

    syntax LockID ::= ".Election"
                    | ".Staking"
                    | ".Democracy"
                    | ".Phragmen"
 // -----------------------------

    syntax AccountLock ::= lock ( id: LockID, until: Int, amount: Int, reasons: Set )
 // ---------------------------------------------------------------------------------

    syntax Bool ::= activeLock (AccountLock, Int, WithdrawReason, Int      ) [function]
                  | activeLocks(Set,         Int, WithdrawReason, Int      ) [function]
                  | activeLocks(List,        Int, WithdrawReason, Int, Bool) [function, klabel(activeLocksAux)]
 // -----------------------------------------------------------------------------------------------------------
    rule activeLock(AL, NOW, REASON, BALANCE) => NOW <Int until(AL) andBool BALANCE <Int amount(AL) andBool REASON in reasons(AL)

    rule activeLocks(ALS, NOW, REASON, BALANCE) => activeLocks(Set2List(ALS), NOW, REASON, BALANCE, false)

    rule activeLocks(.List, _, _, _, RESULT) => RESULT
    rule activeLocks((ListItem(AL) => .List) REST, NOW, REASON, BALANCE, RESULT => RESULT orBool activeLock(AL, NOW, REASON, BALANCE))
```

Slashing and repatriation of reserved balances
==============================================

The first of these is also used by `slash`.

* `slash_reserved`
* `repatriate_reserved`

```k
    syntax Action ::= "slash_reserved" "(" AccountId "," Int ")"
 // ------------------------------------------------------------
    rule [slash-reserved]:
         <k> slash_reserved(ACCOUNT, AMOUNT)
          => set_reserved_balance(ACCOUNT, maxInt(0, RESERVED_BALANCE -Int AMOUNT))
         ...
         </k>
         <accounts>
           <account>
             <accountID> ACCOUNT </accountID>
             <reservedBalance> RESERVED_BALANCE </reservedBalance>
             ...
           </account>
         </accounts>
         <totalIssuance> TOTAL_ISSUANCE => TOTAL_ISSUANCE -Int minInt(RESERVED_BALANCE, AMOUNT) </totalIssuance>

    syntax Action ::= "repatriate_reserved" "(" AccountId "," AccountId "," Int ")"
 // -------------------------------------------------------------------------------
    rule [repatriate-reserved]:
         <k> repatriate_reserved(SLASHED, BENEFICIARY, AMOUNT)
          => set_free_balance(BENEFICIARY, BENEFICIARY_FREE_BALANCE +Int minInt(SLASHED_RESERVED_BALANCE, AMOUNT))
          ~> set_reserved_balance(SLASHED, SLASHED_RESERVED_BALANCE -Int minInt(SLASHED_RESERVED_BALANCE, AMOUNT))
         ...
         </k>
         <accounts>
           <account>
             <accountID> SLASHED </accountID>
             <reservedBalance> SLASHED_RESERVED_BALANCE </reservedBalance>
             ...
           </account>
           <account>
             <accountID> BENEFICIARY </accountID>
             <reservedBalance> BENEFICIARY_RESERVED_BALANCE </reservedBalance>
             <freeBalance> BENEFICIARY_FREE_BALANCE </freeBalance>
             ...
           </account>
         </accounts>
      requires BENEFICIARY_FREE_BALANCE +Int BENEFICIARY_RESERVED_BALANCE >Int 0
```

### Slashing

Used to punish a node for violating the protocol.

```k
    syntax Action ::= "slash" "(" AccountId "," Int ")"
 // ---------------------------------------------------
    rule [slash]:
         <k> slash(ACCOUNT, AMOUNT) => set_free_balance(ACCOUNT, FREE_BALANCE -Int AMOUNT) ... </k>
         <accounts>
           <account>
             <accountID> ACCOUNT </accountID>
             <freeBalance> FREE_BALANCE </freeBalance>
             ...
           </account>
         </accounts>
         <totalIssuance> TOTAL_ISSUANCE => TOTAL_ISSUANCE -Int AMOUNT </totalIssuance>
      requires FREE_BALANCE >=Int AMOUNT

    rule [slash-empty-free]:
         <k> slash(ACCOUNT, AMOUNT)
          => set_free_balance(ACCOUNT, 0)
          ~> slash_reserved(ACCOUNT, AMOUNT -Int FREE_BALANCE)
         ...
         </k>
         <accounts>
           <account>
             <accountID> ACCOUNT </accountID>
             <freeBalance> FREE_BALANCE </freeBalance>
             ...
           </account>
         </accounts>
         <totalIssuance> TOTAL_ISSUANCE => TOTAL_ISSUANCE -Int FREE_BALANCE </totalIssuance>
      requires FREE_BALANCE <Int AMOUNT
```

Reservation and unreservation of balances
=========================================

Used to move balance from free to reserved and visa versa.

```k
    syntax Action ::= reserve ( AccountId , Int )
 // ---------------------------------------------
    rule [reserve]:
         <k> reserve(ACCOUNT, AMOUNT)
          => set_reserved_balance(ACCOUNT, FREE_BALANCE +Int AMOUNT)
          ~> set_free_balance(ACCOUNT, FREE_BALANCE -Int AMOUNT)
         ...
         </k>
         <accounts>
           <account>
             <accountID> ACCOUNT </accountID>
             <freeBalance> FREE_BALANCE </freeBalance>
             <reservedBalance> RESERVED_BALANCE </reservedBalance>
             ...
           </account>
         </accounts>
      requires FREE_BALANCE >=Int AMOUNT
       andBool ensure_can_withdraw(ACCOUNT, Reserve, FREE_BALANCE -Int AMOUNT)

    syntax Action ::= unreserve ( AccountId , Int )
 // -----------------------------------------------
    rule [unreserve]:
         <k> unreserve(ACCOUNT, AMOUNT)
          => set_free_balance(ACCOUNT, FREE_BALANCE +Int minInt(AMOUNT, RESERVED_BALANCE))
          ~> set_reserved_balance(ACCOUNT, FREE_BALANCE -Int minInt(AMOUNT, RESERVED_BALANCE))
         ...
         </k>
         <accounts>
           <account>
             <accountID> ACCOUNT </accountID>
             <freeBalance> FREE_BALANCE </freeBalance>
             <reservedBalance> RESERVED_BALANCE </reservedBalance>
             ...
           </account>
         </accounts>
```

End of module

```k
endmodule
```
