KWasm with Polkadot Host
========================

This module enables calling Polkadot Host host functions from KWasm code.

```k
requires "wasm-text.md"
requires "kwasm-lemmas.md"

module KWASM-POLKADOT-HOST-SYNTAX
    imports KWASM-POLKADOT-HOST
    imports WASM-TEXT-SYNTAX
endmodule

module KWASM-POLKADOT-HOST
    imports K-IO
    imports WASM-TEXT
    imports KWASM-LEMMAS

    configuration
      <polkadot-host>
        <wasm/>
        <k> $PGM:Stmts </k>
        <trace> .List </trace>
      </polkadot-host>

    rule <k> PGM => . </k>
         <instrs> .K => sequenceStmts(text2abstract(PGM)) </instrs>

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
```

### Registering Modules

We will reference modules by name in imports.
`register` is the instruction that allows us to associate a name with a module.

```k
    syntax Stmt ::= "(" "register" WasmString       ")"
                  | "(" "register" WasmString Index ")"
 // ---------------------------------------------------
    rule <instrs> ( register S ) => ( register S (NEXT -Int 1) ) ... </instrs> // Register last instantiated module.
         <nextModuleIdx> NEXT </nextModuleIdx>
      requires NEXT >Int 0

    rule <instrs> ( register S ID:Identifier ) => ( register S IDX ) ... </instrs>
         <moduleIds> ... ID |-> IDX ... </moduleIds>

    rule <instrs> ( register S:WasmString IDX:Int ) => . ... </instrs>
         <moduleRegistry> ... .Map => S |-> IDX ... </moduleRegistry>
```

```k
endmodule
```
