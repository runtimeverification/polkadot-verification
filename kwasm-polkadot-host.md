KWasm with Polkadot Host
========================

This module enables calling Polkadot Host host functions from KWasm code.

```k
requires "test.md"
requires "kwasm-lemmas.md"

module KWASM-POLKADOT-HOST-SYNTAX
    imports KWASM-POLKADOT-HOST
    imports WASM-TEST-SYNTAX
endmodule

module KWASM-POLKADOT-HOST
    imports K-IO
    imports WASM-TEST
    imports KWASM-LEMMAS
    imports MERGED-RULES

    configuration
      <polkadot-host>
        <wasm/>
        <trace> .List </trace>
      </polkadot-host>

    syntax PlainInstr ::= "phost" "." Identifier
 // --------------------------------------------
    rule <k> phost . HOSTCALL => #push(#revs(#zero(FRANGE))) ... </k>
         <trace> ... (.List => ListItem(HOSTCALL)) </trace>
         <moduleRegistry> ... #unparseWasmString("\"env\"") |-> MODID ... </moduleRegistry>
         <moduleInst>
           <modIdx> MODID </modIdx>
           <funcIds> ... HOSTCALL |-> FID ... </funcIds>
           <funcAddrs> ... FID |-> FADDR ... </funcAddrs>
           ...
         </moduleInst>
         <funcDef>
           <fAddr> FADDR </fAddr>
           <fType> _ -> [ FRANGE ] </fType>
           ...
         </funcDef>

    rule #t2aInstr<_>(phost . HOSTCALL) => phost . HOSTCALL

    syntax KItem ::= #push ( ValStack )
 // -----------------------------------
    rule <k> #push(.ValStack) => .              ... </k>
    rule <k> #push(V : VS)    => V ~> #push(VS) ... </k>

    syntax Instr ::= "named_call" "." Identifier [klabel(named_call), symbol]
 // -------------------------------------------------------------------------
    rule <k> named_call . ID => call IDX ... </k>
         <curModIdx> CUR </curModIdx>
         <moduleInst>
           <modIdx> CUR </modIdx>
           <funcIds> ... ID |-> IDX:Int ... </funcIds>
           ...
        </moduleInst>
endmodule
```

Merged Rules
============

This is a set of rules created by identifying common sub-sequences of semantic steps during execution of the `set_free_balance` function.

Most rules could not be used as they were printed, but had to be massaged in the following ways.
-   Remove <generatedTop> cell
-   Remove ellipsis inserted under that cell
-   Remove ensures
-   ~> DotVar\W* => ...
-   #init\([^l]\)locals => #init_locals \1
-   S SS => S SS:Stmts
-   `BOP` => `BOP:IBinOp`,
-   remove `<polkadot-host>`

```k
module MERGED-RULES
    imports WASM-TEST
    
    rule <wasm>
           <k>
                 (     ITYPE0 .const VAL
             ~> ITYPE0 . BOP:IBinOp:IBinOp SS =>     ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 )
             ~> SS )
             ...
           </k>
           <valstack>
             ( < ITYPE0 > C1 : VALSTACK0 => VALSTACK0 )
           </valstack>
           ...
         </wasm>
         requires notBool SS ==K .EmptyStmts andBool false ==K #pow( ITYPE0 ) ==Int 0 andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     #init_locals  N  VALUE0 : VALUE2 : VALSTACK0 =>     #init_locals  N +Int 2  VALSTACK0 )
             ...
           </k>
           <curFrame>
             <locals>
               ( LOCALS => LOCALS [ N <- VALUE0 ] [ N +Int 1 <- VALUE2 ] )
             </locals>
             ...
           </curFrame>
           ...
         </wasm>
         requires true andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     ITYPE .const VAL
             ~> S SS:Stmts =>     S
             ~> SS )
             ...
           </k>
           <valstack>
             ( VALSTACK => < ITYPE > VAL modInt #pow( ITYPE ) : VALSTACK )
           </valstack>
           ...
         </wasm>
         requires notBool SS ==K .EmptyStmts andBool false ==K #pow( ITYPE ) ==Int 0 andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     #init_locals  N  VALUE0 : VALSTACK =>     #init_locals  N +Int 1  VALSTACK )
             ...
           </k>
           <curFrame>
             <locals>
               ( LOCALS => LOCALS [ N <- VALUE0 ] )
             </locals>
             ...
           </curFrame>
           ...
         </wasm>
         requires true andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     ITYPE0 .const VAL ITYPE0 . BOP:IBinOp SS0 =>     ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 )
             ~> SS0 )
             ...
           </k>
           <valstack>
             ( < ITYPE0 > C1 : VALSTACK0 => VALSTACK0 )
           </valstack>
           ...
         </wasm>
         requires notBool SS0 ==K .EmptyStmts andBool false ==K #pow( ITYPE0 ) ==Int 0 andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     V
             ~> S SS:Stmts =>     S
             ~> SS )
             ...
           </k>
           <valstack>
             ( VALSTACK => V : VALSTACK )
           </valstack>
           ...
         </wasm>
         requires notBool V ==K undefined andBool notBool SS ==K .EmptyStmts
```

The following rule required extra massaging:

-   Remove `#Forall` side condition.
-   Change #SemanticCastToInt to regular typing.
-   Dotvar5 in the `<locals>` cell => ... on both sides.

```k
    rule <wasm>
           <k>
                 (     local.get I:Int
             ~> S SS:Stmts =>     S
             ~> SS )
             ...
           </k>
           <valstack>
             ( VALSTACK => VALUE : VALSTACK )
           </valstack>
           <curFrame>
             <locals>
               ... I |-> VALUE ...
             </locals>
             ...
           </curFrame>
           ...
         </wasm>
         requires notBool SS ==K .EmptyStmts andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     local.get I:Int S0 SS0 =>     S0
             ~> SS0 )
             ...
           </k>
           <valstack>
             ( VALSTACK => VALUE : VALSTACK )
           </valstack>
           <curFrame>
             <locals>
               ... I |-> VALUE ...
             </locals>
             ...
           </curFrame>
           ...
         </wasm>
         requires notBool SS0 ==K .EmptyStmts
  andBool true
  [priority(25)]

    rule <wasm>
           <k>
                 (     local.get I:Int ITYPE0 .const VAL ITYPE0 . BOP:IBinOp SS1 =>     ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 )
             ~> SS1 )
             ...
           </k>
           <curFrame>
             <locals>
               ... I |-> < ITYPE0 > C1 ...
             </locals>
             ...
           </curFrame>
           ...
         </wasm>
         requires notBool SS1 ==K .EmptyStmts andBool false ==K #pow( ITYPE0 ) ==Int 0 andBool true
```

```k
endmodule
```
