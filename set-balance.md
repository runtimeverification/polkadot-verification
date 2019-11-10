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
        <creationFee> 0 </creationFee>
        <transferFee> 0 </transferFee>
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

```k
    syntax Action ::= "set_balance_free" "(" AccountId "," Int ")"
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

### `locked_at`

Amount locked at block `n`.


### `transfer`


Transfer some liquid free balance to another account.

`transfer` will set the `FreeBalance` of the sender and receiver.
It will decrease the total issuance of the system by the `TransferFee`.
If the sender's account is below the existential deposit as a result
of the transfer, the account will be reaped.

The dispatch origin for this call must be `Signed` by the transactor.

# <weight>
- Dependent on arguments but not critical, given proper implementations for
  input config types. See related functions below.
- It contains a limited number of reads and writes internally and no complex computation.

Related functions:

  - `ensure_can_withdraw` is always called internally but has a bounded complexity.
  - Transferring balances to accounts that did not exist before will cause
     `T::OnNewAccount::on_new_account` to be called.
  - Removing enough funds from an account will trigger
    `T::DustRemoval::on_unbalanced` and `T::OnFreeBalanceZero::on_free_balance_zero`.

# </weight>

```rust
#[weight = SimpleDispatchInfo::FixedNormal(1_000_000)]
pub fn transfer(
   origin,
   dest: <T::Lookup as StaticLookup>::Source,
   #[compact] value: T::Balance
) {
   let transactor = ensure_signed(origin)?;
   let dest = T::Lookup::lookup(dest)?;
   <Self as Currency<_>>::transfer(&transactor, &dest, value)?;
}
```

```k
    syntax Action ::= "transfer" "(" AccountId "," AccountId "," Int ")"
 // ---------------------------------------------------------------------
    rule [transfer-existing-account]:
         <k> transfer(ORIGIN, DESTINATION, AMOUNT) =>
             set_free_balance(ORIGIN, SOURCE_BALANCE -Int AMOUNT -Int FEE)
             set_free_balance(DESTINATION, DESTINATION_BALANCE +Int AMOUNT)
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
      requires DESTINATION_BALANCE >Int 0 andBool
               #inWidth(64, AMOUNT +Int FEE) andBool
               SOURCE_BALANCE >=Int (AMOUNT +Int FEE)
    rule [transfer-create-account]:
         <k> transfer(ORIGIN, DESTINATION, AMOUNT) =>
             set_free_balance(ORIGIN, SOURCE_BALANCE -Int AMOUNT -Int CREATION_FEE)
             set_free_balance(DESTINATION, AMOUNT)
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
      requires #inWidth(64, AMOUNT +Int CREATION_FEE) andBool
               SOURCE_BALANCE >=Int (AMOUNT +Int CREATION_FEE) andBool
               EXISTENTIAL_DEPOSIT >=Int AMOUNT
```

Force a transfer from any account to any other account.  This can only be done by root.

```k
    syntax Action ::= "force_transfer" "(" AccountId "," AccountId "," AccountId "," Int ")"
 // ----------------------------------------------------------------------------------------
    rule [force-transfer]:
         <k> force_transfer(ORIGIN, SOURCE, DESTINATION, AMOUNT) => transfer(SOURCE, DESTINATION, AMOUNT) </k>
         <root-accounts> ROOTS </root-accounts>
      requires ORIGIN in ROOTS
```


```k
endmodule
```
