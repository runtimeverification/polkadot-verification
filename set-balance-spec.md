Balances Module Specifications
==============================

```k
requires "set-balance.k"

module VERIFICATION
    imports SET-BALANCE

    syntax EntryAction ::= foo ( Int ) | "bar"
    rule <k> foo (X) => bar ... </k> requires X <Int 3
endmodule

module SET-BALANCE-SPEC
    imports VERIFICATION

    rule <k> foo(2) => bar ... </k>
endmodule
```
