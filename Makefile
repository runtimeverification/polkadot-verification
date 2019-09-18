
.PHONY: clean distclean deps deps-polkadot              \
        build build-coverage-llvm specs                 \
        polkadot-runtime-source polkadot-runtime-loaded \
        test test-can-build-specs test-python-config

# Settings
# --------

BUILD_DIR       := .build
DEPS_DIR        := deps
DEFN_DIR        := $(BUILD_DIR)/defn
KWASM_SUBMODULE := $(DEPS_DIR)/wasm-semantics

K_RELEASE := $(KWASM_SUBMODULE)/deps/k/k-distribution/target/release/k
K_BIN     := $(K_RELEASE)/bin
K_LIB     := $(K_RELEASE)/lib

KWASM_DIR  := .
KWASM_MAKE := make --directory $(KWASM_SUBMODULE) BUILD_DIR=../../$(BUILD_DIR)

export K_RELEASE
export KWASM_DIR

PATH := $(CURDIR)/$(KWASM_SUBMODULE):$(CURDIR)/$(K_BIN):$(PATH)
export PATH

PYTHONPATH := $(K_LIB)
export PYTHONPATH

PANDOC_TANGLE_SUBMODULE := $(KWASM_SUBMODULE)/deps/pandoc-tangle
TANGLER                 := $(PANDOC_TANGLE_SUBMODULE)/tangle.lua
LUA_PATH                := $(PANDOC_TANGLE_SUBMODULE)/?.lua;;
export TANGLER
export LUA_PATH

clean:
	rm -rf $(DEFN_DIR) tests/*.out

distclean: clean
	rm -rf $(BUILD_DIR)

deps:
	git submodule update --init --recursive -- $(KWASM_SUBMODULE)
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

KOMPILE_OPTIONS :=

build: build-kwasm-haskell build-kwasm-llvm build-coverage-llvm

# Regular Semantics Build
# -----------------------

build-kwasm-%: $(DEFN_DIR)/kwasm/%/wasm-with-k-term.k
	$(KWASM_MAKE) build-$*                         \
	    DEFN_DIR=../../$(DEFN_DIR)/kwasm           \
	    MAIN_MODULE=WASM-WITH-K-TERM               \
	    MAIN_SYNTAX_MODULE=WASM-WITH-K-TERM-SYNTAX \
	    MAIN_DEFN_FILE=wasm-with-k-term            \
	    KOMPILE_OPTIONS=$(KOMPILE_OPTIONS)

.SECONDARY: $(DEFN_DIR)/kwasm/llvm/wasm-with-k-term.k

$(DEFN_DIR)/kwasm/llvm/%.k: %.md $(TANGLER)
	@mkdir -p $(dir $@)
	pandoc --from markdown --to $(TANGLER) --metadata=code:".k" $< > $@

# Verification Source Build
# -------------------------

CONCRETE_BACKEND := llvm
SYMBOLIC_BACKEND := haskell

polkadot-runtime-source: src/polkadot-runtime.wat
polkadot-runtime-loaded: src/polkadot-runtime.loaded.json

src/polkadot-runtime.loaded.json: src/polkadot-runtime.wat.json
	./kpol run --backend $(CONCRETE_BACKEND) $< --parser cat --output json > $@

src/polkadot-runtime.wat.json: src/polkadot-runtime.env.wat src/polkadot-runtime.wat
	cat $^ | ./kpol kast --backend $(CONCRETE_BACKEND) - json > $@

src/polkadot-runtime.wat: $(POLKADOT_RUNTIME_WASM)
	wasm2wat $< > $@

$(POLKADOT_RUNTIME_WASM):
	git submodule update --init --recursive -- $(POLKADOT_SUBMODULE)
	cd $(POLKADOT_SUBMODULE) && cargo build --package node-template --release

# Generate Execution Traces
# -------------------------

build-coverage-llvm: KOMPILE_OPTIONS+=--coverage
build-coverage-llvm: build-kwasm-llvm

# Specification Build
# -------------------

SPEC_NAMES := set-free-balance

SPECS_DIR := $(BUILD_DIR)/specs
ALL_SPECS := $(patsubst %, $(SPECS_DIR)/%-spec.k, $(SPEC_NAMES))

specs: $(ALL_SPECS)

$(SPECS_DIR)/%-spec.k: %.md
	@mkdir -p $(SPECS_DIR)
	pandoc --from markdown --to $(TANGLER) --metadata=code:.k $< > $@

# Testing
# -------

TEST  := ./kpol
CHECK := git --no-pager diff --no-index --ignore-all-space

test: test-can-build-specs

test-can-build-specs: $(ALL_SPECS:=.can-build)

$(SPECS_DIR)/%-spec.k.can-build: $(SPECS_DIR)/%-spec.k
	kompile --backend $(SYMBOLIC_BACKEND) -I $(SPECS_DIR)                  \
	    --main-module   $(shell echo $* | tr '[:lower:]' '[:upper:]')-SPEC \
	    --syntax-module $(shell echo $* | tr '[:lower:]' '[:upper:]')-SPEC \
	    $<
	rm -rf $*-kompiled

# Python Configuration Build
# --------------------------

test-python-config:
	python3 pykWasm.py
