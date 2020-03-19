KWasm with Polkadot Runtime Environment (PRE)
=============================================

This module enables calling PRE host functions from KWasm code.

```k
requires "test.k"

module KWASM-PRE-SYNTAX
    imports KWASM-PRE
    imports WASM-TEST-SYNTAX
endmodule

module KWASM-PRE
    imports K-IO
    imports WASM-TEST

    configuration
      <polkadot-runtime-environment>
        <wasm/>
        <trace> .List </trace>
      </polkadot-runtime-environment>

    syntax PlainInstr ::= "pre" "." Identifier
 // ------------------------------------------
    rule <k> pre . PRECALL => #push(#revs(#zero(unnameValTypes(FRANGE)))) ... </k>
         <trace> ... (.List => ListItem(PRECALL)) </trace>
         <moduleRegistry> ... "env" |-> MODID ... </moduleRegistry>
         <moduleInst>
           <modIdx> MODID </modIdx>
           <funcIds> FIDS </funcIds>
           <funcAddrs> ... #ContextLookup(FIDS, PRECALL) |-> FADDR ... </funcAddrs>
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
