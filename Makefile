
.PHONY: clean distclean deps deps-polkadot \
        build polkadot-runtime-source \
        can-build-specs \
        test

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
	rustup update nightly
	rustup target add wasm32-unknown-unknown --toolchain nightly
	rustup update stable
	cargo install --git https://github.com/alexcrichton/wasm-gc

# Useful Builds
# -------------

build: build-kwasm-java build-kwasm-haskell build-kwasm-llvm build-kwasm-ocaml

# Regular Semantics Build
# -----------------------

build-kwasm-%:
	$(KWASM_MAKE) build-$* DEFN_DIR=../../$(BUILD_DIR)/defn/kwasm

# Specification Build
# -------------------

SPEC_NAMES := set-free-balance

SPECS_DIR := $(BUILD_DIR)/specs
ALL_SPECS := $(SPECS_DIR)/$(SPEC_NAMES:=-spec.k)

.SECONDARY: $(ALL_SPECS)

can-build-specs: $(ALL_SPECS:=.can-build)

$(SPECS_DIR)/%-spec.k: %.md
	pandoc --from markdown --to $(TANGLER) --metadata=code:.k $< > $@

$(SPECS_DIR)/%-spec.k.can-build: $(SPECS_DIR)/%-spec.k
	kompile --backend haskell $<
	rm -rf $*-kompiled

# Verification Source Build
# -------------------------

polkadot-runtime-source: src/polkadot-runtime.wat.json

src/polkadot-runtime.wat.json: src/polkadot-runtime.wat
	./kpol kast --backend llvm $< json > $@

src/polkadot-runtime.wat: $(POLKADOT_RUNTIME_WASM)
	wasm2wat $< > $@

$(POLKADOT_RUNTIME_WASM):
	git submodule update --init --recursive -- $(POLKADOT_SUBMODULE)
	cd $(POLKADOT_SUBMODULE) && cargo build --package node-template --release

# Testing
# -------

TEST                  := ./kpol
CHECK                 := git --no-pager diff --no-index --ignore-all-space
TEST_CONCRETE_BACKEND := llvm
