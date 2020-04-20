KWasm with Polkadot Host
========================

This module enables calling Polkadot Host host functions from KWasm code.

```k
requires "test.k"
requires "kwasm-lemmas.k"

module KWASM-POLKADOT-HOST-SYNTAX
    imports KWASM-POLKADOT-HOST
    imports WASM-TEST-SYNTAX
endmodule

module KWASM-POLKADOT-HOST
    imports K-IO
    imports WASM-TEST
    imports KWASM-LEMMAS

    configuration
      <polkadot-host>
        <wasm/>
        <trace> .List </trace>
      </polkadot-host>

    syntax PlainInstr ::= "phost" "." Identifier
 // --------------------------------------------
    rule <k> phost . HOSTCALL => #push(#revs(#zero(unnameValTypes(FRANGE)))) ... </k>
         <trace> ... (.List => ListItem(HOSTCALL)) </trace>
         <moduleRegistry> ... #unparseWasmString("\"env\"") |-> MODID ... </moduleRegistry>
         <moduleInst>
           <modIdx> MODID </modIdx>
           <funcIds> FIDS </funcIds>
           <funcAddrs> ... #ContextLookup(FIDS, HOSTCALL) |-> FADDR ... </funcAddrs>
           ...
         </moduleInst>
         <funcDef>
           <fAddr> FADDR </fAddr>
           <fType> _ -> [ FRANGE ] </fType>
           ...
         </funcDef>

    syntax KItem ::= #push ( ValStack )
 // -----------------------------------
    rule <k> #push(.ValStack) => .              ... </k>
    rule <k> #push(V : VS)    => V ~> #push(VS) ... </k>
endmodule
```
