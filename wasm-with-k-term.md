KWasm with K-TERM
=================

**TODO**: This module is a HACK to get unparsing to work correctly.

```k
requires "test.k"

module WASM-WITH-K-TERM-SYNTAX
    imports WASM-WITH-K-TERM
    imports WASM-TEST-SYNTAX
endmodule

module WASM-WITH-K-TERM
    imports WASM-TEST
    imports K-TERM
    imports K-IO
endmodule
```
