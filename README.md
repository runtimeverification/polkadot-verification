Polkadot Module Verification
============================

**UNDER CONSTRUCTION**

### Useful links

-   Polkadot Runtime Environment (PRE): <https://wiki.polkadot.network/en/latest/polkadot/learn/PRE/>
-   Balances module: <https://github.com/paritytech/substrate/blob/master/srml/balances/src/lib.rs>
-   Polkadot Spec: <https://github.com/w3f/polkadot-re-spec/blob/master/polkadot_re_spec.pdf>
    See "Runtime Environment API" for external function specs (eg. `ext_malloc` and `ext_blake`).

### Building/Installation/Setup

Make sure you have all the dependencies of KWasm installed: <https://github.com/kframework/wasm-semantics>.

Then the following (roughly) is what you need to do to build KWasm for this repository.

```sh
git submodule update --init --recursive
make deps
make build -j2 KOMPILE_OPTIONS='"--emit-json --coverage"' SUBDEFN=coverage
make build -j2 KOMPILE_OPTIONS='"--emit-json"'
```

Setup `PATH` and `PYTHONPATH`:

```sh
export PATH=./deps/wasm-semantics/deps/k/k-distribution/target/release/k/bin:$PATH
export PYTHONPATH=./deps/wasm-semantics/deps/k/k-distribution/target/release/k/lib
```

Then generate the haskell coverage file:

```sh
make deps/wasm-semantics/tests/simple/constants.wast.coverage-haskell
```

Then try merging the rules:

```sh
./mergeRules.py deps/wasm-semantics/tests/simple/constants.wast.coverage-haskell 2
```

Which results in errors in `definition.kore` due to multiple symbols with the same klabel (for `EmptyK` and `EmptyKList`).
Edit `definition.kore` directly to fix it, then re-run the above command.
