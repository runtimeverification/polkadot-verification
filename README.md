branch: dev

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
make build -j2 KOMPILE_OPTIONS='--coverage' SUBDEFN=coverage
make build -j2
```

Setup `PATH` and `PYTHONPATH`:

```sh
export PATH=./deps/wasm-semantics/deps/k/k-distribution/target/release/k/bin:$PATH
export PYTHONPATH=./deps/wasm-semantics/deps/k/k-distribution/target/release/k/lib
```

Then try merging rules for a given test:

```sh
make test-merge-rules -j8
```
