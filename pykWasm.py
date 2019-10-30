#!/usr/bin/env python3

import difflib
import json
import pyk
import sys

from pyk.kast import KApply, KConstant, KRewrite, KSequence, KToken, KVariable, _notif, _warning, _fatal

################################################################################
# Should be Upstreamed                                                         #
################################################################################

def kompile_definition(definition_dir, backend, main_defn_file, main_module, kompileArgs = [], teeOutput = True, kRelease = None):
    command = 'kompile'
    if kRelease is not None:
        command = kRelease + '/bin/' + command
    elif 'K_RELEASE' in os.environ:
        command = os.environ['K_RELEASE'] + '/bin/' + command
    kCommand = [ command , '--backend' , backend , '--directory' , definition_dir , '-I' , definition_dir , '--main-module' , main_module , main_defn_file ] + kompileArgs
    _notif('Running: ' + ' '.join(kCommand))
    return pyk._teeProcessStdout(kCommand, tee = teeOutput)

################################################################################
# Load Definition Specific Stuff                                               #
################################################################################

WASM_definition_llvm_no_coverage_dir = '.build/defn/kwasm/llvm'
WASM_definition_llvm_coverage_dir    = '.build/defn/coverage/llvm'

WASM_definition_haskell_no_coverage_dir = '.build/defn/kwasm/haskell'
WASM_definition_haskell_coverage_dir    = '.build/defn/coverage/haskell'

WASM_definition_llvm_no_coverage = pyk.readKastTerm(WASM_definition_llvm_no_coverage_dir + '/wasm-with-k-term-kompiled/compiled.json')
WASM_definition_llvm_coverage    = pyk.readKastTerm(WASM_definition_llvm_coverage_dir + '/wasm-with-k-term-kompiled/compiled.json')

WASM_definition_haskell_no_coverage = pyk.readKastTerm(WASM_definition_haskell_no_coverage_dir + '/wasm-with-k-term-kompiled/compiled.json')
WASM_definition_haskell_coverage    = pyk.readKastTerm(WASM_definition_haskell_coverage_dir + '/wasm-with-k-term-kompiled/compiled.json')

WASM_symbols_llvm_no_coverage = pyk.buildSymbolTable(WASM_definition_llvm_no_coverage)
WASM_symbols_llvm_coverage    = pyk.buildSymbolTable(WASM_definition_llvm_coverage)

WASM_symbols_haskell_no_coverage = pyk.buildSymbolTable(WASM_definition_haskell_no_coverage)
WASM_symbols_haskell_coverage    = pyk.buildSymbolTable(WASM_definition_haskell_coverage)

# Custom unparsers for some symbols
# WASM_symbols [ '.ValStack_WASM-DATA_'                                               ] = pyk.constLabel('.ValStack')
# WASM_symbols [ '.Int_WASM-DATA_'                                                    ] = pyk.constLabel('.Int')
# WASM_symbols [ '.ModuleInstCellMap'                                                 ] = pyk.constLabel('.ModuleInstCellMap')
# WASM_symbols [ '.FuncDefCellMap'                                                    ] = pyk.constLabel('.FuncDefCellMap')
# WASM_symbols [ '.TabInstCellMap'                                                    ] = pyk.constLabel('.TabInstCellMap')
# WASM_symbols [ '.MemInstCellMap'                                                    ] = pyk.constLabel('.MemInstCellMap')
# WASM_symbols [ '.GlobalInstCellMap'                                                 ] = pyk.constLabel('.GlobalInstCellMap')
# WASM_symbols [ 'ModuleInstCellMapItem'                                              ] = (lambda a1, a2: a2)
# WASM_symbols [ '___WASM__Stmt_Stmts'                                                ] = (lambda a1, a2: a1 + '\n' + a2)
# WASM_symbols [ '___WASM__Defn_Defns'                                                ] = (lambda a1, a2: a1 + '\n' + a2)
# WASM_symbols [ '___WASM__Instr_Instrs'                                              ] = (lambda a1, a2: a1 + '\n' + a2)
# WASM_symbols [ '.List{"___WASM__Stmt_Stmts_Stmts"}_Stmts'                           ] = pyk.constLabel('')
# WASM_symbols [ '.List{"___WASM__EmptyStmt_EmptyStmts_EmptyStmts"}_EmptyStmts'       ] = pyk.constLabel('')
# WASM_symbols [ '.List{"___WASM-DATA__ValType_ValTypes_ValTypes"}_ValTypes'          ] = pyk.constLabel('')
# WASM_symbols [ '.List{"___WASM__TypeDecl_TypeDecls_TypeDecls"}_TypeDecls'           ] = pyk.constLabel('')
# WASM_symbols [ '.List{"___WASM__LocalDecl_LocalDecls_LocalDecls"}_LocalDecls'       ] = pyk.constLabel('')
# WASM_symbols [ '.List{"___WASM-DATA__Index_ElemSegment_ElemSegment"}_ElemSegment'   ] = pyk.constLabel('')
# WASM_symbols [ '.List{"___WASM-DATA__WasmString_DataString_DataString"}_DataString' ] = pyk.constLabel('')
# WASM_symbols [ '(module__)_WASM__OptionalId_Defns'                                  ] = (lambda mName, mDefns: '(module ' + mName + '\n' + pyk.indent(mDefns) + '\n)')
# WASM_symbols [ '(func__)_WASM__OptionalId_FuncSpec'                                 ] = (lambda funcName, funcSpec: '(func ' + funcName + '\n' + pyk.indent(funcSpec) + '\n)')
# WASM_symbols [ '____WASM__TypeUse_LocalDecls_Instrs'                                ] = (lambda type, locals, instrs: '\n'.join([type, locals, instrs]))

################################################################################
# Runner Wrappers                                                              #
################################################################################

def kast(inputJson, *kastArgs):
    return pyk.kastJSON('.build/defn/kwasm/llvm', inputJson, kastArgs = list(kastArgs), kRelease = 'deps/wasm-semantics/deps/k/k-distribution/target/release/k')

def krun(inputJson, *krunArgs):
    return pyk.krunJSON('.build/defn/kwasm/llvm', inputJson, krunArgs = list(krunArgs), kRelease = 'deps/wasm-semantics/deps/k/k-distribution/target/release/k')

def kprove(inputJson, *krunArgs):
    return pyk.kproveJSON('.build/defn/kwasm/llvm', inputJson, kproveArgs = list(kproveArgs), kRelease = 'deps/wasm-semantics/deps/k/k-distribution/target/release/k')

################################################################################
# Main Functionality                                                           #
################################################################################

def get_init_config():
    init_term = { 'format': 'KAST', 'version': 1, 'term': KConstant('.List{"___WASM_Stmts_Stmt_Stmts"}_Stmts') }
    (_, simple_config, _) = krun(init_term)
    return pyk.splitConfigFrom(simple_config)

if __name__ == '__main__':
    (generatedTop, initSubst) = get_init_config()
    initial_configuration = pyk.substitute(generatedTop, initSubst)
    kast_json = { 'format': 'KAST', 'version': 1, 'term': initial_configuration }

    # Use official K unparser to get string for initial configuration
    (returnCode, kastPrinted, _) = kast(kast_json, '--input', 'json', '--output', 'pretty')
    if returnCode != 0:
        _fatal('kast returned non-zero exit code reading/printing the initial configuration')
        sys.exit(returnCode)

    # Use fast pyk unparser to get string for initial configuration
    fastPrinted = pyk.prettyPrintKast(initial_configuration['args'][0], WASM_symbols_llvm_no_coverage)
    _notif('fastPrinted output')
    print(fastPrinted)

    # Check that fast and official unparsers agree, or see how much they disagree.
    kastPrinted = kastPrinted.strip()
    if fastPrinted != kastPrinted:
        _warning('kastPrinted and fastPrinted differ!')
        for line in difflib.unified_diff(kastPrinted.split('\n'), fastPrinted.split('\n'), fromfile='kast', tofile='fast', lineterm='\n'):
            sys.stderr.write(line + '\n')
        sys.stderr.flush()

