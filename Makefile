
.PHONY: clean distclean deps deps-polkadot polkadot-runtime build

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
	rm -rf $(DEFN_DIR)

distclean: clean
	rm -rf $(BUILD_DIR)

deps:
	git submodule update --init --recursive
	$(KWASM_MAKE) deps

# Polkadot Setup
# --------------

POLKADOT_SUBMODULE := $(DEPS_DIR)/substrate
POLKADOT_RUNTIME_WASM := $(POLKADOT_SUBMODULE)/target/debug/wbuild/target/wasm32-unknown-unknown/debug/node_runtime.wasm

deps-polkadot:
	curl https://sh.rustup.rs -sSf | sh
	rustup update nightly
	rustup target add wasm32-unknown-unknown --toolchain nightly
	rustup update stable
	cargo install --git https://github.com/alexcrichton/wasm-gc

polkadot-runtime: polkadot-runtime.wat

polkadot-runtime.wat: $(POLKADOT_RUNTIME_WASM)
	wasm2wat $< > $@

$(POLKADOT_RUNTIME_WASM):
	git submodule update --init -- $(POLKADOT_SUBMODULE)
	cd $(POLKADOT_SUBMODULE) && cargo build

# Useful Builds
# -------------

build: build-kwasm-java build-kwasm-haskell

# Regular Semantics Build
# -----------------------

build-kwasm-%:
	$(KWASM_MAKE) build-$* DEFN_DIR=../../$(BUILD_DIR)/defn/kwasm
