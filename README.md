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
./deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/bin/k-configure-opam-dev
make deps
make build -j4
```
