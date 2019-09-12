#!/usr/bin/env python3

import difflib
import json
import pyk
import sys

from pyk.kast import KApply, KConstant, KSequence, KToken, KVariable, _notif, _warning, _fatal

underbarUnparsingInModule = lambda modName, inputString: pyk.underbarUnparsing(inputString.split('_' + modName)[0])

WASM_symbols = { '.List{"___WASM__Stmt_Stmts"}_Stmts'                 : pyk.constLabel('.Stmts')
               , '.ValStack_WASM-DATA_'                               : pyk.constLabel('.ValStack')
               , '.Int_WASM-DATA_'                                    : pyk.constLabel('.Int')
               , '.ModuleInstCellMap'                                 : pyk.constLabel('.ModuleInstCellMap')
               , '.FuncDefCellMap'                                    : pyk.constLabel('.FuncDefCellMap')
               , '.TabInstCellMap'                                    : pyk.constLabel('.TabInstCellMap')
               , '.MemInstCellMap'                                    : pyk.constLabel('.MemInstCellMap')
               , '.GlobalInstCellMap'                                 : pyk.constLabel('.GlobalInstCellMap')
               , 'ModuleInstCellMapItem'                              : (lambda a1, a2: a2)
               , '___WASM__Stmt_Stmts'                                : (lambda a1, a2: a1 + '\n' + a2)
               , '___WASM__Defn_Defns'                                : (lambda a1, a2: a1 + '\n' + a2)
               , '___WASM__Instr_Instrs'                              : (lambda a1, a2: a1 + '\n' + a2)
               , '.List{"___WASM__EmptyStmt_EmptyStmts"}_EmptyStmts'  : pyk.constLabel('')
               , '.List{"___WASM-DATA__ValType_ValTypes"}_ValTypes'   : pyk.constLabel('')
               , '.List{"___WASM__TypeDecl_TypeDecls"}_TypeDecls'     : pyk.constLabel('')
               , '(module__)_WASM__OptionalId_Defns'                  : (lambda mName, mDefns: '(module ' + mName + '\n' + pyk.indent(mDefns) + '\n)')
               , '(func__)_WASM__OptionalId_FuncSpec'                 : (lambda funcName, funcSpec: '(func ' + funcName + '\n' + pyk.indent(funcSpec) + '\n)')
               , '____WASM__TypeUse_LocalDecls_Instrs'                : (lambda type, locals, instrs: '\n'.join([type, locals, instrs]))
               }

WASM_DATA_underbar_unparsed_symbols = [ 'func_WASM-DATA_'
                                      , '___WASM-DATA__ValType_ValTypes'
                                      , 'i32_WASM-DATA_'
                                      , 'i64_WASM-DATA_'
                                      , 'f32_WASM-DATA_'
                                      , 'f64_WASM-DATA_'
                                      ]

for symb in WASM_DATA_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-DATA', symb)

WASM_underbar_unparsed_symbols = [ '(import___)_WASM__WasmString_WasmString_ImportDesc'
                                 , '(func__)_WASM__OptionalId_TypeUse'
                                 , '(type_)_WASM__Index'
                                 , '(export_(_))_WASM__WasmString_Externval'
                                 , '___WASM-DATA__AllocatedKind_Index'
                                 , '(type_(func_))_WASM__OptionalId_TypeDecls'
                                 , '___WASM__TypeDecl_TypeDecls'
                                 , '___WASM__TypeKeyWord_ValTypes'
                                 , '_WASM-DATA_'
                                 , 'param_WASM_'
                                 , 'result_WASM_'
                                 , '(invoke_)_WASM__Int'
                                 , '_.const__WASM__IValType_Int'
                                 ]

for symb in WASM_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM', symb)

WASM_TEST_underbar_unparsed_symbols = [ '(register_)_WASM-TEST__WasmString'
                                      ]

for symb in WASM_TEST_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-TEST', symb)

WASM_TEXT_underbar_unparsed_symbols = [ '(_)_WASM-TEXT__PlainInstr'
                                      ]

for symb in WASM_TEXT_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-TEXT', symb)

ALL_symbols = pyk.combineDicts(pyk.K_symbols, WASM_symbols)

def kast(inputJson, *kastArgs):
    return pyk.kastJSON('.build/defn/kwasm/llvm', inputJson, kastArgs = list(kastArgs), kRelease = 'deps/wasm-semantics/deps/k/k-distribution/target/release/k')

def krun(inputJson, *krunArgs):
    return pyk.krunJSON('.build/defn/kwasm/llvm', inputJson, krunArgs = list(krunArgs), kRelease = 'deps/wasm-semantics/deps/k/k-distribution/target/release/k')

def kprove(inputJson, *krunArgs):
    return pyk.kproveJSON('.build/defn/kwasm/llvm', inputJson, kproveArgs = list(kproveArgs), kRelease = 'deps/wasm-semantics/deps/k/k-distribution/target/release/k')

def split_symbolic_config_from(configuration):
    initial_substitution = {}

    _mkCellVar = lambda label: label.replace('-', '_').replace('<', '').replace('>', '').upper() + '_CELL'

    def _replaceWithVar(k):
        if pyk.isKApply(k) and pyk.isCellKLabel(k['label']):
            if len(k['args']) == 1 and not (pyk.isKApply(k['args'][0]) and pyk.isCellKLabel(k['args'][0]['label'])):
                config_var = _mkCellVar(k['label'])
                initial_substitution[config_var] = k['args'][0]
                return KApply(k['label'], [KVariable(config_var)])
        return k

    pyk.traverseBottomUp(configuration, _replaceWithVar)
    return (configuration, initial_substitution)

init_term = { 'format': 'KAST', 'version': 1, 'term': KConstant('.List{"___WASM__Stmt_Stmts"}_Stmts') }
(_, simple_config, _) = krun(init_term, '--parser', 'cat')
(generatedTop, initSubst) = split_symbolic_config_from(simple_config)

if __name__ == '__main__':
    initial_configuration = pyk.substitute(generatedTop, initSubst)
    kast_json = { 'format': 'KAST', 'version': 1, 'term': initial_configuration }

    (returnCode, kastPrinted, _) = kast(kast_json, '--input', 'json', '--output', 'pretty')
    if returnCode != 0:
        _fatal('kast returned non-zero exit code reading/printing the initial configuration')
        sys.exit(returnCode)

    fastPrinted = pyk.prettyPrintKast(initial_configuration['args'][0], ALL_symbols)
    _notif('fastPrinted output')
    print(fastPrinted)

    kastPrinted = kastPrinted.strip()
    if fastPrinted != kastPrinted:
        _warning('kastPrinted and fastPrinted differ!')
        for line in difflib.unified_diff(kastPrinted.split('\n'), fastPrinted.split('\n'), fromfile='kast', tofile='fast', lineterm='\n'):
            sys.stderr.write(line + '\n')
        sys.stderr.flush()

