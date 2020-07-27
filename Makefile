
.PHONY: all clean distclean deps deps-polkadot          \
        build                                           \
        polkadot-runtime-source polkadot-runtime-loaded \
        prove-specs defn-specs kompile-specs            \
        test test-python-config test-search

# Settings
# --------

BUILD_DIR       := .build
DEPS_DIR        := deps
DEFN_DIR        := $(BUILD_DIR)/defn
KWASM_SUBMODULE := $(DEPS_DIR)/wasm-semantics
K_SUBMODULE     := $(KWASM_SUBMODULE)/deps/k

ifneq (,$(wildcard $(K_SUBMODULE)/k-distribution/target/release/k/bin/*))
    K_RELEASE ?= $(abspath $(K_SUBMODULE)/k-distribution/target/release/k)
else
    K_RELEASE ?= $(dir $(shell which kompile))..
endif
K_BIN := $(K_RELEASE)/bin
K_LIB := $(K_RELEASE)/lib/kframework
export K_RELEASE

KWASM_DIR  := .
KWASM_MAKE := make --directory $(KWASM_SUBMODULE) BUILD_DIR=../../$(BUILD_DIR) RELEASE=$(RELEASE)

export KWASM_DIR

PATH := $(K_BIN):$(CURDIR)/$(KWASM_SUBMODULE):$(PATH)
export PATH

PYTHONPATH := $(K_LIB)
export PYTHONPATH

PANDOC_TANGLE_SUBMODULE := $(abspath $(DEPS_DIR)/pandoc-tangle)
TANGLER                 := $(PANDOC_TANGLE_SUBMODULE)/tangle.lua
LUA_PATH                := $(PANDOC_TANGLE_SUBMODULE)/?.lua;;
export TANGLER
export LUA_PATH

KPOL := ./kpol

all: build

clean:
	rm -rf $(DEFN_DIR) tests/*.out

distclean: clean
	rm -rf $(BUILD_DIR)

deps:
	$(KWASM_MAKE) deps

# Polkadot Setup
# --------------

POLKADOT_SUBMODULE    := $(DEPS_DIR)/substrate
POLKADOT_RUNTIME_WASM := $(POLKADOT_SUBMODULE)/target/release/wbuild/node-template-runtime/node_template_runtime.compact.wasm

# Useful Builds
# -------------

KOMPILE_OPTS := --emit-json

MAIN_MODULE        := MERGED
MAIN_SYNTAX_MODULE := KWASM-POLKADOT-HOST-SYNTAX
MAIN_DEFN_FILE     := merged
EXTRA_FILES        := kwasm-polkadot-host

ifeq (coverage,$(BUILD))
    KOMPILE_OPTS += --coverage
    SUBDEFN      := coverage
else
    SUBDEFN := kwasm
endif

export SUBDEFN

build: build-llvm build-haskell

# Semantics Build
# ---------------

build-%: $(patsubst %, $(KWASM_SUBMODULE)/%.md, $(MAIN_DEFN_FILE) $(EXTRA_FILES))
	$(KWASM_MAKE) build-$*                               \
	    DEFN_DIR=../../$(DEFN_DIR)/$(SUBDEFN)            \
	    llvm_main_module=$(MAIN_MODULE)                  \
	    llvm_syntax_module=$(MAIN_SYNTAX_MODULE)         \
	    llvm_main_file=$(MAIN_DEFN_FILE)                 \
	    haskell_main_module=$(MAIN_MODULE)               \
	    haskell_syntax_module=$(MAIN_SYNTAX_MODULE)      \
	    haskell_main_file=$(MAIN_DEFN_FILE)              \
	    EXTRA_SOURCE_FILES=$(MAIN_DEFN_FILE).md          \
	    KOMPILE_OPTS="$(KOMPILE_OPTS)"

$(KWASM_SUBMODULE)/%.md: %.md
	cp $< $@

# Verification Source Build
# -------------------------

CONCRETE_BACKEND := llvm
SYMBOLIC_BACKEND := haskell

POLKADOT_RUNTIME_WAT         := src/polkadot-runtime.wat
POLKADOT_RUNTIME_ENV_WAT     := src/polkadot-runtime.env.wat
POLKADOT_RUNTIME_JSON        := src/polkadot-runtime.wat.json
POLKADOT_RUNTIME_LOADED_JSON := src/polkadot-runtime.loaded.json

polkadot-runtime-source: $(POLKADOT_RUNTIME_WAT)
polkadot-runtime-loaded: $(POLKADOT_RUNTIME_LOADED_JSON)

$(POLKADOT_RUNTIME_WASM):
	cd $(POLKADOT_SUBMODULE) && cargo build --package node-template --release

$(POLKADOT_RUNTIME_WAT): $(POLKADOT_RUNTIME_WASM)
	@mkdir -p src
	wasm2wat $< | sed 's/(elem/;; (elem/' > $@

$(POLKADOT_RUNTIME_ENV_WAT): $(POLKADOT_RUNTIME_WAT)
	./build-runtime-host.sh $< > $@

$(POLKADOT_RUNTIME_LOADED_JSON): $(POLKADOT_RUNTIME_JSON)
	$(KPOL) run --backend $(CONCRETE_BACKEND) $< --parser cat --output json > $@

$(POLKADOT_RUNTIME_JSON): $(POLKADOT_RUNTIME_ENV_WAT) $(POLKADOT_RUNTIME_WAT)
	cat $^ | $(KPOL) kast --backend $(CONCRETE_BACKEND) - json > $@

# Specification Build
# -------------------

SPEC_NAMES := set-balance

SPECS_DIR      := $(BUILD_DIR)/specs
SPECS_SOURCE   := $(patsubst %, %.md, $(SPEC_NAMES))
SPECS_PROOFS   := $(patsubst %, $(SPECS_DIR)/%-spec.k, $(SPEC_NAMES))
SPECS_KOMPILED := $(patsubst %, $(SPECS_DIR)/%-kompiled/definition.kore, $(SPEC_NAMES))

defn-specs:    $(SPECS_SOURCE)
kompile-specs: $(SPECS_KOMPILED)
prove-specs:   $(SPECS_PROOFS:=.prove)

$(SPECS_DIR)/%-kompiled/definition.kore: %.md
	kompile --backend $(SYMBOLIC_BACKEND) -I $(CURDIR)                \
	    --main-module   $(shell echo $* | tr '[:lower:]' '[:upper:]') \
	    --syntax-module $(shell echo $* | tr '[:lower:]' '[:upper:]') \
	    --directory $(SPECS_DIR)                                      \
	    $<

$(SPECS_DIR)/%-spec.k.prove: $(SPECS_DIR)/%-spec.k $(SPECS_DIR)/%-kompiled/definition.kore
	kprove --directory $(SPECS_DIR) $(SPECS_DIR)/$*-spec.k --def-module VERIFICATION

$(SPECS_DIR)/%-spec.k: %-spec.md $(TANGLER)
	@mkdir -p $(dir $@)
	pandoc --from markdown --to $(TANGLER) --metadata=code:.k $< > $@

# Testing
# -------

CHECK := git --no-pager diff --no-index --ignore-all-space

test: prove-specs test-python-config test-search

# Search Through Executions
# -------------------------

test-search:
	python3 search.py summary

# Python Configuration Build
# --------------------------

test-python-config:
	python3 pykWasm.py
