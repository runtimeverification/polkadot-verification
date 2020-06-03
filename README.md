Polkadot Module Verification
============================

**UNDER CONSTRUCTION**

### Useful links

-   Polkadot Runtime Environment (PRE): <https://wiki.polkadot.network/en/latest/polkadot/learn/PRE/>
-   Balances module: <https://github.com/paritytech/substrate/blob/master/srml/balances/src/lib.rs>
-   Polkadot Spec: <https://github.com/w3f/polkadot-spec/blob/master/runtime-environment-spec/polkadot_re_spec.pdf>
    See "Runtime Environment API" for external function specs (eg. `ext_malloc` and `ext_blake`).

### Building/Installation/Setup

Make sure you have all the dependencies of KWasm installed: <https://github.com/kframework/wasm-semantics>.

Then the following (roughly) is what you need to do to build KWasm for this repository.

```sh
git submodule update --init --recursive
make deps
make build -j2 BUILD=coverage
make build -j2
```

Setup `PATH` and `PYTHONPATH`:

```sh
export PATH=./deps/wasm-semantics/deps/k/k-distribution/target/release/k/bin:$PATH
export PYTHONPATH=./deps/wasm-semantics/deps/k/k-distribution/target/release/k/lib/kframework
```

Then try merging rules for a given test:

```sh
make test-merge-rules -j8
```

### Updating Source Files

Dependencies:

-   [WABT](https://github.com/WebAssembly/wabt).

Several files are too large to re-generate every time, so they are committed under the `src/` directory.
They depend on the version of Substrate committed at `deps/substrate`.
The files are:

-   `src/polkadot-runtime.wat`: Wasm sources of Substrate, modified to work with the KWasm parser.
-   `src/polkadot-runtime.env.wat`: Type signatures of Polkadot Host in a module named `"env"` (extracted from Substrate sources).
-   `src/polkadot-runtime.wat.json`: K JSON parse AST of Wasm sources of Substrate (including the Polkadot Host Wasm module).
-   `src/polkadot-runtime.loaded.json`: K JSON AST of Polkadot-Wasm configuration with Substrate sources loaded into memory (and empty `<k>` cell).

When updating the Substrate submodule, you need to update the files under `src/` which the Makefile can assist with.
**NO GUARANTEES** that the procedure using by the `Makefile` correctly builds the needed source files.
To build just the `src/polkadot-runtime.wat` file that will be used as the Substrate source, run:

```sh
make polkadot-runtime-source
```

To build all the `src/` files, run:

```sh
make polkadot-runtime-loaded
```

