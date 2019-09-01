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

If you don't have `rustup`, get it with (likely if you've used other K projects or worked on Substrate you already have it):

```sh
curl https://sh.rustup.rs -sSf | sh -s -- -y
```

Then the following (roughly) is what you need to do to build KWasm for this repository.

```sh
git submodule update --init --recursive
./deps/wasm-semantics/deps/k/llvm-backend/src/main/native/llvm-backend/install-rust
./deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/bin/k-configure-opam-dev
make deps
make build -j4
```
