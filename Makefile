
.PHONY: clean distclean deps deps-polkadot \
        polkadot-runtime build \
        test test-build-products test-polkadot-runtime test-parse

# Settings
# --------

BUILD_DIR:=.build
DEPS_DIR:=deps
DEFN_DIR:=$(BUILD_DIR)/defn
KWASM_SUBMODULE:=$(DEPS_DIR)/wasm-semantics

K_RELEASE := $(KWASM_SUBMODULE)/deps/k/k-distribution/target/release/k
K_BIN     := $(K_RELEASE)/bin
K_LIB     := $(K_RELEASE)/lib

KWASM_DIR  := .
KWASM_MAKE := make --directory $(KWASM_SUBMODULE) BUILD_DIR=../../$(BUILD_DIR)

export K_RELEASE
export KWASM_DIR

PATH:=$(CURDIR)/$(KWASM_SUBMODULE):$(CURDIR)/$(K_BIN):$(PATH)
export PATH

PANDOC_TANGLE_SUBMODULE:=$(KWASM_SUBMODULE)/deps/pandoc-tangle
TANGLER:=$(PANDOC_TANGLE_SUBMODULE)/tangle.lua
LUA_PATH:=$(PANDOC_TANGLE_SUBMODULE)/?.lua;;
export TANGLER
export LUA_PATH

clean:
	rm -rf $(DEFN_DIR) tests/*.out

distclean: clean
	rm -rf $(BUILD_DIR)

deps:
	git submodule update --init --recursive
	$(KWASM_MAKE) deps

# Polkadot Setup
# --------------

POLKADOT_SUBMODULE    := $(DEPS_DIR)/substrate
POLKADOT_RUNTIME_WASM := $(POLKADOT_SUBMODULE)/target/release/wbuild/node-template-runtime/node_template_runtime.compact.wasm

deps-polkadot:
	curl https://sh.rustup.rs -sSf | sh -s -- -y
	rustup update nightly
	rustup target add wasm32-unknown-unknown --toolchain nightly
	rustup update stable
	cargo install --git https://github.com/alexcrichton/wasm-gc

polkadot-runtime: $(POLKADOT_RUNTIME_WASM)

$(POLKADOT_RUNTIME_WASM):
	git submodule update --init --recursive -- $(POLKADOT_SUBMODULE)
	cd $(POLKADOT_SUBMODULE) && cargo build --package node-template --release

# Useful Builds
# -------------

build: build-kwasm-java build-kwasm-haskell build-kwasm-llvm build-kwasm-ocaml

# Regular Semantics Build
# -----------------------

build-kwasm-%:
	$(KWASM_MAKE) build-$* DEFN_DIR=../../$(BUILD_DIR)/defn/kwasm

# Testing
# -------

TEST                  := ./kpol
CHECK                 := git --no-pager diff --no-index --ignore-all-space
TEST_CONCRETE_BACKEND := llvm

test: test-build-products

### Polkadot Runtime Build Products

# The files `tests/polkadot-runtime.{wat,wat.json}` take a lot of resources to produce.
# They are committed to the repository, and on CI we check that their generation process produces the same files.

test-build-products: test-polkadot-runtime test-parse

test-polkadot-runtime: $(POLKADOT_RUNTIME_WASM)
	wasm2wat $< > tests/polkadot-runtime.wat.out
	$(CHECK) tests/polkadot-runtime.wat tests/polkadot-runtime.wat.out
	rm -rf tests/polkadot-runtime.wat.out

test-parse: tests/polkadot-runtime.wat tests/polkadot-runtime.wat.json build-kwasm-$(TEST_CONCRETE_BACKEND)
	$(TEST) kast --backend $(TEST_CONCRETE_BACKEND) $< json > $<.json.out
	$(CHECK) $<.json $<.json.out
	rm -rf $<.json.out
