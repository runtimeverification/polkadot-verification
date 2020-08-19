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

### Performing Rule Merges

Make sure you have `PATH` and `PYTHONPATH` set as above.

You can get help with `./search.py --help`.

You can try to do productivity rule merging on the input using:

```sh
./search.py summary
```

To profile which rule merges are slow, you can use the `profile` mode of `search.py`.
For example, the following runs all batches of 10 rules 3 times each, and prints out the ones that are more than 0.8 standard deviations away from the mean merge time.

```sh
./search.py profile -n 1 -w 10 -r 3 -d 0.8 &> search_profile
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

### Proving High-Level Specifications

The `*-spec.md` files contain high-level specifications of the system behavior.
The definition file containing the semantics for the proofs must be put in a file with the same name but without the `-spec` suffix; i.e. the semantics used to prove `foo-spec.md` are placed in `foo.md`.
The `*-spec.md` file must contain a module called `VERIFICATION` which imports the semantics module.
See the structure of `set-balance-spec.md` and `set-balance.md` for an example.

To run the prover on all specifications, run:

```
make prove-specs
```
