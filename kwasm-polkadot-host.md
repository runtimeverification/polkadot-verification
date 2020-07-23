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
    rule <instrs> phost . HOSTCALL => #push(#revs(#zero(FRANGE))) ... </instrs>
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
    rule <instrs> #push(.ValStack) => .              ... </instrs>
    rule <instrs> #push(V : VS)    => V ~> #push(VS) ... </instrs>

    syntax Instr ::= "named_call" "." Identifier [klabel(named_call), symbol]
 // -------------------------------------------------------------------------
    rule <instrs> named_call . ID => call IDX ... </instrs>
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

Merged rules
------------

```k
rule <polkadot-host>
       <wasm>
         <instrs>
               (     #init_locals N VALUE0 : VALSTACK =>     #init_locals N +Int 1 VALSTACK ) ...
         </instrs>
         <curFrame>
           <locals>
             ( LOCALS => LOCALS [ N <- VALUE0 ] )
           </locals>
           ...
         </curFrame>
         ...
       </wasm>
       ...
     </polkadot-host>
  
  
   [priority(25)]
```


-   Added `:StoreOp`.

```k
rule <polkadot-host>
       <wasm>
         <instrs>
               (     < ITYPE > VAL
           ~> ITYPE . SOP:StoreOp =>     ITYPE . SOP IDX VAL ) ...
         </instrs>
         <valstack>
           ( < i32 > IDX : VALSTACK0 => VALSTACK0 )
         </valstack>
         ...
       </wasm>
       ...
     </polkadot-host>
  
  
   [priority(25)]
```


```k
rule <polkadot-host>
       <wasm>
         <instrs>
               (     ITYPE .const VAL => .K ) ...
         </instrs>
         <valstack>
           ( VALSTACK => < ITYPE > VAL modInt #pow( ITYPE ) : VALSTACK )
         </valstack>
         ...
       </wasm>
       ...
     </polkadot-host>
  requires #pow( ITYPE ) =/=Int 0
  
   [priority(25)]
```

```k
rule <polkadot-host>
       <wasm>
         <instrs>
               (     #init_locals N VALUE0 : VALUE2 : VALSTACK0 =>     #init_locals N +Int 2 VALSTACK0 ) ...
         </instrs>
         <curFrame>
           <locals>
             ( LOCALS => LOCALS [ N <- VALUE0 ] [ N +Int 1 <- VALUE2 ] )
           </locals>
           ...
         </curFrame>
         ...
       </wasm>
       ...
     </polkadot-host>
  
  
   [priority(25)]
```

```k
endmodule
```


```
rule <polkadot-host>
       <wasm>
         <instrs>
               (     ITYPE0 .const VAL
           ~> ITYPE0 . BOP => .K ) ...
         </instrs>
         <valstack>
           ( < ITYPE0 > C1 : VALSTACK1 => ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) : VALSTACK1 )
         </valstack>
         ...
       </wasm>
       ...
     </polkadot-host>
  requires ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) =/=K undefined andBool #Ceil( ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) ) andBool #pow( ITYPE0 ) =/=Int 0
  
   [priority(25)]
```

```
rule <polkadot-host>
       <wasm>
         <instrs>
               (     ITYPE0 .const VAL
           ~> ITYPE0 . BOP
           ~> local.tee I => .K ) ...
         </instrs>
         <valstack>
           ( < ITYPE0 > C1 : VALSTACK1 => ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) : VALSTACK1 )
         </valstack>
         <curFrame>
           <locals>
             ( DotVar12 I |-> _37 => DotVar12 I |-> ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) )
           </locals>
           ...
         </curFrame>
         ...
       </wasm>
       ...
     </polkadot-host>
  requires ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) =/=K undefined andBool #Ceil( ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) ) andBool notBool #SemanticCastToInt ( I ) in_keys( DotVar12 ) andBool #pow( ITYPE0 ) =/=Int 0
  
   [priority(25)]
```

```
rule <polkadot-host>
       <wasm>
         <instrs>
               (     local.get I
           ~> call IDX =>     (invoke FADDR ) ) ...
         </instrs>
         <valstack>
           ( VALSTACK => VALUE : VALSTACK )
         </valstack>
         <curFrame>
           <locals>
             DotVar5 I |-> VALUE
           </locals>
           <curModIdx>
             CUR
           </curModIdx>
           ...
         </curFrame>
         <moduleInstances>
           ModuleInstCellMapItem( <modIdx>
             CUR
           </modIdx> , <moduleInst>
             <modIdx>
               CUR
             </modIdx>
             <funcAddrs>
               DotVar9 IDX |-> FADDR
             </funcAddrs>
             ...
           </moduleInst> ) DotVar8
         </moduleInstances>
         ...
       </wasm>
       ...
     </polkadot-host>
  requires notBool <modIdx>
     CUR
   </modIdx> in DotVar8 keys( ) andBool notBool #SemanticCastToInt ( I ) in_keys( DotVar5 ) andBool notBool #SemanticCastToInt ( IDX ) in_keys( DotVar9 )
  
   [priority(25)]
```
