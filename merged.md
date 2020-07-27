
```k
requires "kwasm-polkadot-host.md"

module MERGED
    imports KWASM-POLKADOT-HOST
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

-   Remove `#Ceil` side condition on binary operation (it goes away if the numeric functions are made total).
-   Add `:IBinOp`.

```k
rule <polkadot-host>
       <wasm>
         <instrs>
               (     ITYPE0 .const VAL
           ~> ITYPE0 . BOP:IBinOp => .K ) ...
         </instrs>
         <valstack>
           ( < ITYPE0 > C1 : VALSTACK1 => ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) : VALSTACK1 )
         </valstack>
         ...
       </wasm>
       ...
     </polkadot-host>
  requires ITYPE0 . BOP C1 VAL modInt #pow( ITYPE0 ) =/=K undefined andBool #pow( ITYPE0 ) =/=Int 0

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
