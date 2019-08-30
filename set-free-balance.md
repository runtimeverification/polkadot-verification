`set_free_balance` spec
=======================

The Rust code is here:

```
/// Set the free balance of an account to some new value. Will enforce `ExistentialDeposit`
/// law, annulling the account as needed.
///
/// Doesn't do any preparatory work for creating a new account, so should only be used when it
/// is known that the account already exists.
///
/// NOTE: LOW-LEVEL: This will not attempt to maintain total issuance. It is expected that
/// the caller will do this.
fn set_free_balance(who: &T::AccountId, balance: T::Balance) -> UpdateBalanceOutcome {
  // Commented out for now - but consider it instructive.
  // assert!(!Self::total_balance(who).is_zero());
  // assert!(Self::free_balance(who) > T::ExistentialDeposit::get());
  if balance < T::ExistentialDeposit::get() {
    <FreeBalance<T, I>>::insert(who, balance);
    Self::on_free_too_low(who);
    UpdateBalanceOutcome::AccountKilled
  } else {
    <FreeBalance<T, I>>::insert(who, balance);
    UpdateBalanceOutcome::Updated
  }
}
```

State Model
-----------

```k
module SET-FREE-BALANCE-SPEC
    imports WASM-TEST

    configuration
      <set-free-balance>
        <update> $UPDATE:Update </update>
        <events> .List </events>
        <existentialDeposit> 0 </existentialDeposit>
        <accounts>
          <account multiplicity="*" type="Map">
            <accountID> .AccountId:AccountId </accountID>
            <balance> 0 | 0 </balance>
            <nonce> .Nonce </nonce>
          </account>
        </accounts>
      </set-free-balance>
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

### `set_free_balance`

-   Updates an accounts balance if the new balance is above the existential threshold.
-   Kills the account if the balance goes below the existential threshold and the reserved balance is non-zero.
-   Reaps the account if the balance goes below the existential threshold and the reserved balance is zero.

```k

    syntax Action ::= set_free_balance ( AccountId , Int )
 // ------------------------------------------------------
    rule [account-updated]:
         <k> set_free_balance(WHO, BALANCE) => Updated ... </k>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <acctID> WHO </acctID>
           <balance> (_ => 0) | _ </balance>
           ...
         </account>
      requires EXISTENTIAL_DEPOSIT <=Int BALANCE

    rule [account-killed]:
         <k> set_free_balance(WHO, BALANCE) => AccountKilled ... </k>
         <events> ... (.List => ListItem(DustEvent(FREE_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <account>
           <acctID> WHO </acctID>
           <nonce> _ => .NoNonce </nonce>
           <balance> (FREE_BALANCE => 0) | RESERVED_BALANCE </balance>
           ...
         </account>
      requires BALANCE <Int EXISTENTIAL_DEPOSIT
       andBool 0 <Int RESERVED_BALANCE

    rule [account-reaped]:
         <k> set_free_balance(WHO, BALANCE) => AccountKilled ... </k>
         <events> ... (.List => ListItem(DustEvent(FREE_BALANCE))) </events>
         <existentialDeposit> EXISTENTIAL_DEPOSIT </existentialDeposit>
         <accounts>
           ( <account>
               <acctID> WHO </acctID>
               <balance> FREE_BALANCE | 0 </balance>
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
