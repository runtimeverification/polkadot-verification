#!/usr/bin/env python3

import difflib
import json
import pyk
import sys

from pyk.kast import KApply, KConstant, KSequence, KToken, KVariable, _notif, _warning, _fatal

################################################################################
# Unparsing                                                                    #
################################################################################

# Builds an unparser based on the KLabel directly, interpreting the `_` as argument positions for unparsing.
# First strips the module name suffix off the label.
underbarUnparsingInModule = lambda modName, inputString: pyk.underbarUnparsing(inputString.split('_' + modName)[0])

WASM_symbols = { '.ValStack_WASM-DATA_'                                    : pyk.constLabel('.ValStack')
               , '.Int_WASM-DATA_'                                         : pyk.constLabel('.Int')
               , '.ModuleInstCellMap'                                      : pyk.constLabel('.ModuleInstCellMap')
               , '.FuncDefCellMap'                                         : pyk.constLabel('.FuncDefCellMap')
               , '.TabInstCellMap'                                         : pyk.constLabel('.TabInstCellMap')
               , '.MemInstCellMap'                                         : pyk.constLabel('.MemInstCellMap')
               , '.GlobalInstCellMap'                                      : pyk.constLabel('.GlobalInstCellMap')
               , 'ModuleInstCellMapItem'                                   : (lambda a1, a2: a2)
               , '___WASM__Stmt_Stmts'                                     : (lambda a1, a2: a1 + '\n' + a2)
               , '___WASM__Defn_Defns'                                     : (lambda a1, a2: a1 + '\n' + a2)
               , '___WASM__Instr_Instrs'                                   : (lambda a1, a2: a1 + '\n' + a2)
               , '.List{"___WASM__Stmt_Stmts"}_Stmts'                      : pyk.constLabel('')
               , '.List{"___WASM__EmptyStmt_EmptyStmts"}_EmptyStmts'       : pyk.constLabel('')
               , '.List{"___WASM-DATA__ValType_ValTypes"}_ValTypes'        : pyk.constLabel('')
               , '.List{"___WASM__TypeDecl_TypeDecls"}_TypeDecls'          : pyk.constLabel('')
               , '.List{"___WASM__LocalDecl_LocalDecls"}_LocalDecls'       : pyk.constLabel('')
               , '.List{"___WASM-DATA__Index_ElemSegment"}_ElemSegment'    : pyk.constLabel('')
               , '.List{"___WASM-DATA__WasmString_DataString"}_DataString' : pyk.constLabel('')
               , '(module__)_WASM__OptionalId_Defns'                       : (lambda mName, mDefns: '(module ' + mName + '\n' + pyk.indent(mDefns) + '\n)')
               , '(func__)_WASM__OptionalId_FuncSpec'                      : (lambda funcName, funcSpec: '(func ' + funcName + '\n' + pyk.indent(funcSpec) + '\n)')
               , '____WASM__TypeUse_LocalDecls_Instrs'                     : (lambda type, locals, instrs: '\n'.join([type, locals, instrs]))
               }

WASM_DATA_underbar_unparsed_symbols = [ 'func_WASM-DATA_'
                                      , '___WASM-DATA__ValType_ValTypes'
                                      , 'i32_WASM-DATA_'
                                      , 'i64_WASM-DATA_'
                                      , 'f32_WASM-DATA_'
                                      , 'f64_WASM-DATA_'
                                      , '___WASM-DATA__Index_ElemSegment'
                                      , '___WASM-DATA__Int_Int'
                                      , '___WASM-DATA__WasmString_DataString'
                                      , 'global_WASM-DATA_'
                                      , 'memory_WASM-DATA_'
                                      , 'table_WASM-DATA_'
                                      ]

for symb in WASM_DATA_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-DATA', symb)

WASM_NUMERIC_underbar_unparsed_symbols = [ 'sub_WASM-NUMERIC_'
                                         , 'eqz_WASM-NUMERIC_'
                                         , 'add_WASM-NUMERIC_'
                                         , 'and_WASM-NUMERIC_'
                                         , 'eq_WASM-NUMERIC_'
                                         , 'ne_WASM-NUMERIC_'
                                         , 'extend_i32_u_WASM-NUMERIC_'
                                         , 'div_u_WASM-NUMERIC_'
                                         , 'gt_u_WASM-NUMERIC_'
                                         , 'le_s_WASM-NUMERIC_'
                                         , 'lt_s_WASM-NUMERIC_'
                                         , 'lt_u_WASM-NUMERIC_'
                                         , 'mul_WASM-NUMERIC_'
                                         , 'shl_WASM-NUMERIC_'
                                         , 'mul_WASM-NUMERIC_'
                                         , 'shr_u_WASM-NUMERIC_'
                                         , 'wrap_i64_WASM-NUMERIC_'
                                         , 'or_WASM-NUMERIC_'
                                         , 'ge_s_WASM-NUMERIC_'
                                         , 'ge_u_WASM-NUMERIC_'
                                         , 'gt_s_WASM-NUMERIC_'
                                         , 'le_u_WASM-NUMERIC_'
                                         , 'rem_s_WASM-NUMERIC_'
                                         , 'rem_u_WASM-NUMERIC_'
                                         , 'shr_s_WASM-NUMERIC_'
                                         , 'xor_WASM-NUMERIC_'
                                         , 'clz_WASM-NUMERIC_'
                                         , 'ctz_WASM-NUMERIC_'
                                         , 'div_s_WASM-NUMERIC_'
                                         , 'ge_u_WASM-NUMERIC_'
                                         , 'gt_s_WASM-NUMERIC_'
                                         , 'le_u_WASM-NUMERIC_'
                                         , 'popcnt_WASM-NUMERIC_'
                                         , 'rem_u_WASM-NUMERIC_'
                                         , 'shr_s_WASM-NUMERIC_'
                                         , 'xor_WASM-NUMERIC_'
                                         ]

for symb in WASM_NUMERIC_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-NUMERIC', symb)

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
                                 , 'call__WASM__Index'
                                 , 'unreachable_WASM_'
                                 , '(type_)__WASM__Index_TypeDecls'
                                 , '___WASM__LocalDecl_LocalDecls'
                                 , 'local__WASM__ValTypes'
                                 , 'global.get__WASM__Index'
                                 , 'global.set__WASM__Index'
                                 , 'local.tee__WASM__Index'
                                 , 'local.set__WASM__Index'
                                 , 'local.get__WASM__Index'
                                 , '_.__WASM__IValType_IBinOp'
                                 , 'block__end_WASM__TypeDecls_Instrs'
                                 , '_.__WASM__IValType_TestOp'
                                 , 'br_if__WASM__Index'
                                 , '_.__WASM__IValType_LoadOpM'
                                 , '_.__WASM__IValType_StoreOpM'
                                 , '___WASM__LoadOp_MemArg'
                                 , '___WASM__StoreOp_MemArg'
                                 , 'load_WASM_'
                                 , 'store_WASM_'
                                 , '___WASM__OffsetArg_AlignArg'
                                 , 'align=__WASM__Int'
                                 , 'offset=__WASM__Int'
                                 , 'br__WASM__Index'
                                 , 'i32 . store8_WASM_'
                                 , 'load8_u_WASM_'
                                 , 'loop__end_WASM__TypeDecls_Instrs'
                                 , 'return_WASM_'
                                 , 'store8_WASM_'
                                 , '_.__WASM__IValType_IRelOp'
                                 , 'br_table__WASM__ElemSegment'
                                 , 'select_WASM_'
                                 , '_.__WASM__AValType_CvtOp'
                                 , '_.__WASM__IValType_IUnOp'
                                 , 'call_indirect__WASM__TypeUse'
                                 , '(data__)_WASM__Offset_DataString'
                                 , 'drop_WASM_'
                                 , '(elem__)_WASM__Offset_ElemSegment'
                                 , 'funcref_WASM_'
                                 , '(global__)_WASM__OptionalId_GlobalSpec'
                                 , 'i32 . load16_u_WASM_'
                                 , 'i32 . load8_s_WASM_'
                                 , 'i32 . store16_WASM_'
                                 , 'i64 . load16_u_WASM_'
                                 , 'i64 . load32_u_WASM_'
                                 , 'i64 . store16_WASM_'
                                 , 'i64 . store32_WASM_'
                                 , '(memory__)_WASM__OptionalId_MemorySpec'
                                 , '(mut_)_WASM__AValType'
                                 , '(table__)_WASM__OptionalId_TableSpec'
                                 , '___WASM__Limits_TableElemType'
                                 , '___WASM__TextFormatGlobalType_Instr'
                                 , 'load16_u_WASM_'
                                 , 'load32_u_WASM_'
                                 , 'load8_s_WASM_'
                                 , 'store16_WASM_'
                                 , 'store32_WASM_'
                                 ]

for symb in WASM_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM', symb)

WASM_TEST_underbar_unparsed_symbols = [ '(register_)_WASM-TEST__WasmString'
                                      ]

for symb in WASM_TEST_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-TEST', symb)

WASM_TEXT_underbar_unparsed_symbols = [ '(_)_WASM-TEXT__PlainInstr'
                                      , '___WASM-TEXT__InlineExport_FuncSpec'
                                      , '(export_)_WASM-TEXT__WasmString'
                                      ]

for symb in WASM_TEXT_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-TEXT', symb)

ALL_symbols = pyk.combineDicts(pyk.K_symbols, WASM_symbols)

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
# Should be upstreamed into pyk                                                #
################################################################################

def splitConfigFrom(configuration):
    """Split the substitution from a given configuration.

    Given an input configuration `config`, will return a tuple `(symbolic_config, subst)`, where:

        1.  `config == substitute(symbolic_config, subst)`
        2.  `symbolic_config` is the same configuration structure, but where the contents of leaf cells is replaced with a fresh KVariable.
        3.  `subst` is the substitution for the generated KVariables back to the original configuration contents.
    """
    initial_substitution = {}
    _mkCellVar = lambda label: label.replace('-', '_').replace('<', '').replace('>', '').upper() + '_CELL'
    def _replaceWithVar(k):
        if pyk.isKApply(k) and pyk.isCellKLabel(k['label']):
            if len(k['args']) == 1 and not (pyk.isKApply(k['args'][0]) and pyk.isCellKLabel(k['args'][0]['label'])):
                config_var = _mkCellVar(k['label'])
                initial_substitution[config_var] = k['args'][0]
                return KApply(k['label'], [KVariable(config_var)])
        return k
    symbolic_config = pyk.traverseBottomUp(configuration, _replaceWithVar)
    return (symbolic_config, initial_substitution)

################################################################################
# Main Functionality                                                           #
################################################################################

def get_init_config():
    init_term = { 'format': 'KAST', 'version': 1, 'term': KConstant('.List{"___WASM__Stmt_Stmts"}_Stmts') }
    (_, simple_config, _) = krun(init_term)
    return splitConfigFrom(simple_config)

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
    fastPrinted = pyk.prettyPrintKast(initial_configuration['args'][0], ALL_symbols)
    _notif('fastPrinted output')
    print(fastPrinted)

    # Check that fast and official unparsers agree, or see how much they disagree.
    kastPrinted = kastPrinted.strip()
    if fastPrinted != kastPrinted:
        _warning('kastPrinted and fastPrinted differ!')
        for line in difflib.unified_diff(kastPrinted.split('\n'), fastPrinted.split('\n'), fromfile='kast', tofile='fast', lineterm='\n'):
            sys.stderr.write(line + '\n')
        sys.stderr.flush()

