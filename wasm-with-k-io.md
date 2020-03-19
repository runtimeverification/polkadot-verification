KWasm with K-IO
===============

**TODO**: This module is a HACK to get coverage to work properly.

```k
requires "test.k"

module WASM-WITH-K-IO-SYNTAX
    imports WASM-WITH-K-IO
    imports WASM-TEST-SYNTAX
endmodule

module WASM-WITH-K-IO
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
