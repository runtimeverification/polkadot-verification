
.PHONY: clean distclean deps deps-polkadot                       \
        build                                                    \
        polkadot-runtime-source polkadot-runtime-loaded          \
        prove-specs defn-specs kompile-specs                     \
        test test-python-config test-rule-lists test-merge-rules \
        test-merge-all-rules test-search

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
KWASM_MAKE := make --directory $(KWASM_SUBMODULE) BUILD_DIR=../../$(BUILD_DIR) K_RELEASE=../../$(K_RELEASE)

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

KPOL := ./kpol

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
	cargo install --git https://github.com/alexcrichton/wasm-gc

# Useful Builds
# -------------

KOMPILE_OPTIONS :=

MAIN_MODULE        := KWASM-PRE
MAIN_SYNTAX_MODULE := KWASM-PRE-SYNTAX
MAIN_DEFN_FILE     := kwasm-pre

SUBDEFN := kwasm
export SUBDEFN

build: build-llvm build-haskell

# Semantics Build
# ---------------

build-%: $(DEFN_DIR)/$(SUBDEFN)/%/$(MAIN_DEFN_FILE).k
	$(KWASM_MAKE) build-$*                               \
	    DEFN_DIR=../../$(DEFN_DIR)/$(SUBDEFN)            \
	    MAIN_MODULE=$(MAIN_MODULE)                       \
	    MAIN_SYNTAX_MODULE=$(MAIN_SYNTAX_MODULE)         \
	    MAIN_DEFN_FILE=$(MAIN_DEFN_FILE)                 \
	    KOMPILE_OPTIONS="--emit-json $(KOMPILE_OPTIONS)"

.SECONDARY: $(DEFN_DIR)/$(SUBDEFN)/llvm/$(MAIN_DEFN_FILE).k    \
            $(DEFN_DIR)/$(SUBDEFN)/haskell/$(MAIN_DEFN_FILE).k

$(DEFN_DIR)/$(SUBDEFN)/llvm/%.k: %.md $(TANGLER)
	@mkdir -p $(dir $@)
	pandoc --from markdown --to $(TANGLER) --metadata=code:".k" $< > $@

$(DEFN_DIR)/$(SUBDEFN)/haskell/%.k: %.md $(TANGLER)
	@mkdir -p $(dir $@)
	pandoc --from markdown --to $(TANGLER) --metadata=code:".k" $< > $@

# Verification Source Build
# -------------------------

CONCRETE_BACKEND := llvm
SYMBOLIC_BACKEND := haskell

polkadot-runtime-source: src/polkadot-runtime.wat
polkadot-runtime-loaded: src/polkadot-runtime.loaded.json

src/polkadot-runtime.loaded.json: src/polkadot-runtime.wat.json
	$(KPOL) run --backend $(CONCRETE_BACKEND) $< --parser cat --output json > $@

src/polkadot-runtime.wat.json: src/polkadot-runtime.env.wat src/polkadot-runtime.wat
	cat $^ | $(KPOL) kast --backend $(CONCRETE_BACKEND) - json > $@

src/polkadot-runtime.wat: $(POLKADOT_RUNTIME_WASM)
	wasm2wat $< > $@

$(POLKADOT_RUNTIME_WASM):
	git submodule update --init --recursive -- $(POLKADOT_SUBMODULE)
	cd $(POLKADOT_SUBMODULE) && cargo build --package node-template --release

# Generate Execution Traces
# -------------------------

MERGE_RULES_TECHNIQUE := max-productivity

# TODO: Hacky way for selecting coverage file.
.SECONDARY: deps/wasm-semantics/tests/simple/integers.wast.coverage-llvm
$(KWASM_SUBMODULE)/tests/simple/%.wast.coverage-$(CONCRETE_BACKEND): $(KWASM_SUBMODULE)/tests/simple/%.wast
	rm -rf $@-dir
	mkdir -p $@-dir
	K_LOG_DIR=$@-dir SUBDEFN=coverage $(KPOL) run --backend $(CONCRETE_BACKEND) $<
	mv $@-dir/*_coverage.txt $@
	rm -rf $@-dir

$(KWASM_SUBMODULE)/tests/simple/%.wast.coverage-$(SYMBOLIC_BACKEND): $(KWASM_SUBMODULE)/tests/simple/%.wast.coverage-$(CONCRETE_BACKEND)
	./translateCoverage.py $(DEFN_DIR)/coverage/$(CONCRETE_BACKEND)/$(MAIN_DEFN_FILE)-kompiled \
	                       $(DEFN_DIR)/kwasm/$(SYMBOLIC_BACKEND)/$(MAIN_DEFN_FILE)-kompiled    \
	                       $< > $@

$(KWASM_SUBMODULE)/tests/simple/%.wast.merged-rules: $(KWASM_SUBMODULE)/tests/simple/%.wast.coverage-$(SYMBOLIC_BACKEND)
	./mergeRules.py $(MERGE_RULES_TECHNIQUE) $< > $@

# Specification Build
# -------------------

SPEC_NAMES := set-balance

SPECS_DIR      := $(BUILD_DIR)/specs
SPECS_SOURCE   := $(patsubst %, $(SPECS_DIR)/%.k, $(SPEC_NAMES))
SPECS_PROOFS   := $(patsubst %, $(SPECS_DIR)/%-spec.k, $(SPEC_NAMES))
SPECS_KOMPILED := $(patsubst %, $(SPECS_DIR)/%-kompiled/definition.kore, $(SPEC_NAMES))

defn-specs:    $(SPECS_SOURCE)
kompile-specs: $(SPECS_KOMPILED)
prove-specs:   $(SPECS_PROOFS:=.prove)

$(SPECS_DIR)/%.k: %.md
	@mkdir -p $(SPECS_DIR)
	pandoc --from markdown --to $(TANGLER) --metadata=code:.k $< > $@

$(SPECS_DIR)/%-kompiled/definition.kore: $(SPECS_DIR)/%.k
	kompile --backend $(SYMBOLIC_BACKEND) -I $(SPECS_DIR)             \
	    --main-module   $(shell echo $* | tr '[:lower:]' '[:upper:]') \
	    --syntax-module $(shell echo $* | tr '[:lower:]' '[:upper:]') \
	    -I $(K_RELEASE)/include/builtin                               \
	    $<

$(SPECS_DIR)/%-spec.k.prove: $(SPECS_DIR)/%-spec.k $(SPECS_DIR)/%-kompiled/definition.kore
	kprove --directory $(SPECS_DIR) $< --def-module VERIFICATION

# Testing
# -------

CHECK := git --no-pager diff --no-index --ignore-all-space

test: test-merge-rules prove-specs test-python-config test-search

all_simple_tests := $(wildcard $(KWASM_SUBMODULE)/tests/simple/*.wast)
bad_simple_tests := $(KWASM_SUBMODULE)/tests/simple/arithmetic.wast     \
                    $(KWASM_SUBMODULE)/tests/simple/bitwise.wast        \
                    $(KWASM_SUBMODULE)/tests/simple/comparison.wast     \
                    $(KWASM_SUBMODULE)/tests/simple/constants.wast      \
                    $(KWASM_SUBMODULE)/tests/simple/control-flow.wast   \
                    $(KWASM_SUBMODULE)/tests/simple/functions_call.wast \
                    $(KWASM_SUBMODULE)/tests/simple/memory.wast         \
                    $(KWASM_SUBMODULE)/tests/simple/polymorphic.wast
simple_tests     := $(filter-out $(bad_simple_tests), $(all_simple_tests))

test-rule-lists: $(simple_tests:=.coverage-$(SYMBOLIC_BACKEND))
test-merge-rules: $(simple_tests:=.merged-rules)
test-merge-all-rules: $(KWASM_SUBMODULE)/tests/simple/merge-all-rules

$(KWASM_SUBMODULE)/tests/simple/merge-all-rules: $(simple_tests:=.coverage-$(SYMBOLIC_BACKEND))
	./mergeRules.py $(MERGE_RULES_TECHNIQUE) $^ > $@

# Search Through Executions
# -------------------------

test-search:
	python3 search.py

# Python Configuration Build
# --------------------------

test-python-config:
	python3 pykWasm.py
