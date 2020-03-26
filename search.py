#!/usr/bin/env python3

import pyk
import random
import sys

from pykWasm import *
from pykWasm import _fatal, _notif, _warning

from mergeRules import *

sys.setrecursionlimit(1500000000)

function_names = [ '$pallet_balances::Module<T_I>::set_free_balance::h143784e9433faed6'
                 , '$pallet_balances::Module<T_I>::call_functions::h5c8befb10787dea0'
                 , '$pallet_balances::Module<T_I>::storage_metadata::h082815e2817e5c19'
                 , '$pallet_balances::Module<T_I>::module_constants_metadata::h487a5f31fed8642e'
                 ]

function_name = function_names[0]

wasm_push   = lambda type, value: KApply('(_)_WASM-TEXT_FoldedInstr_PlainInstr', [KApply('_.const__WASM_PlainInstr_IValType_Int', [KConstant(type + '_WASM-DATA_IValType'), value])])
wasm_call   = lambda fname: KApply('(_)_WASM-TEXT_FoldedInstr_PlainInstr', [KApply('call__WASM_PlainInstr_Index', [KToken(fname, 'IdentifierToken')])])
wasm_invoke = lambda fid: KApply('(invoke_)_WASM_Instr_Int', [KToken(str(fid), 'Int')])

def wasm_stmts_join(stmtType = 'Stmt'):
    return '___WASM_' + stmtType + 's_' + stmtType + '_' + stmtType + 's'

def wasm_stmts_unit():
    return '.List{"___WASM_EmptyStmts_EmptyStmt_EmptyStmts"}_EmptyStmts'

def wasm_stmts(vs, stmtType = 'Stmt'):
    if len(vs) == 0:
        return KConstant(wasm_stmts_unit())
    inst  = vs[0]
    insts = vs[1:]
    return KApply(wasm_stmts_join(stmtType = stmtType), [inst, wasm_stmts(insts)])

def wasm_stmts_flattened(stmts, stmtType = 'Stmt'):
    if not pyk.isKApply(stmts):
        _fatal('Must be a KApply')
    if stmts['label'] == wasm_stmts_join(stmtType = stmtType):
        return [ stmts['args'][0] ] + wasm_stmts_flattened(stmts['args'][1])
    elif stmts['label'] == wasm_stmts_unit():
        return []
    else:
        _fatal('Not of type ' + stmtType + '!')

loaded_program = pyk.readKastTerm('src/polkadot-runtime.loaded.json')
(symbolic_config, init_subst) = pyk.splitConfigFrom(loaded_program)

invoking_steps = [ wasm_push('i32', KVariable('V1'))
                 , wasm_push('i64', KVariable('V2'))
                 , wasm_push('i64', KVariable('V3'))
                 , wasm_call(function_name)
                 ]

invokingSubstitution = { 'V1' : KToken(str(random.randint(0, 2 ** 32)), 'Int')
                       , 'V2' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                       , 'V3' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                       }

init_subst['K_CELL'] = pyk.substitute(KSequence(invoking_steps), invokingSubstitution)
print(pyk.prettyPrintKast(init_subst['K_CELL'], WASM_symbols_llvm_no_coverage))
init_config = pyk.substitute(symbolic_config, init_subst)

coverageFile = krunCoverage({ 'format' : 'KAST' , 'version': 1, 'term': init_config }, '--term')
ruleSeq = pyk.translateCoverageFromPaths(WASM_definition_llvm_coverage_dir + '/' + WASM_definition_main_file + '-kompiled', WASM_definition_haskell_no_coverage_dir + '/' + WASM_definition_main_file + '-kompiled', coverageFile)
mergedRules = merge_rules_max_productivity(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, [ruleSeq], min_merged_success_rate = 0.25, min_occurance_rate = 0.05)
print()
for mr in mergedRules:
    print('Merged Rule:')
    print('============')
    print()
    print(prettyPrintRule(mr, WASM_symbols_haskell_no_coverage))
print()
sys.stdout.flush()
sys.stderr.flush()
