#!/usr/bin/env python3

import argparse
import pyk
import random
import resource
import sys

from pykWasm import *
from pykWasm import _fatal, _notif, _warning

from mergeRules import *

sys.setrecursionlimit(1500000000)
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

function_names = []
with open('src/polkadot-runtime.wat', 'r') as src:
    for line in src:
        if 'func $pallet_balances' in line:
            function_names.append(line.split()[1])

set_free_balance_function_name = [ fname for fname in function_names if 'set_free_balance' in fname ][0]
print('Function name: ' + set_free_balance_function_name)

wasm_push   = lambda type, value: KApply('(_)_WASM-TEXT_FoldedInstr_PlainInstr', [KApply('_.const__WASM_PlainInstr_IValType_WasmInt', [KConstant(type + '_WASM-DATA_IValType'), value])])
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
                 , wasm_call(set_free_balance_function_name)
                 ]

searchArgs = argparse.ArgumentParser()
searchArgs.add_argument('-n', '--num-runs', type = int, default = 1, help = 'Number of random runs to use as input.')

searchCommandParsers = searchArgs.add_subparsers(dest = 'command')

summaryArgs = searchCommandParsers.add_parser('summary', help = 'Try to produce summaries of the executions.')

args = vars(searchArgs.parse_args())

if args['command'] == 'summary':
    numExec = args['num_runs']
    ruleSeqs = set([])
    for i in range(numExec):
        invokingSubstitution = { 'V1' : KToken(str(random.randint(0, 2 ** 32)), 'Int')
                               , 'V2' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                               , 'V3' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                               }
        init_subst['K_CELL'] = pyk.substitute(KSequence(invoking_steps), invokingSubstitution)
        # print(pyk.prettyPrintKast(init_subst['K_CELL'], WASM_symbols_llvm_no_coverage))
        init_config = pyk.substitute(symbolic_config, init_subst)
        coverageFile = krunCoverage({ 'format' : 'KAST' , 'version': 1, 'term': init_config }, '--term')
        ruleSeq = pyk.translateCoverageFromPaths(WASM_definition_llvm_coverage_dir + '/' + WASM_definition_main_file + '-kompiled', WASM_definition_haskell_no_coverage_dir + '/' + WASM_definition_main_file + '-kompiled', coverageFile)
        ruleSeqs.add('|'.join(ruleSeq))

    ruleSeqs = [ ruleSeq.split('|') for ruleSeq in ruleSeqs ]
    ruleMerges = merge_rules_max_productivity(ruleSeqs, min_merged_success_rate = 0.25, min_occurance_rate = 0.05)
    mergedRules = tryMergeRules(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, ruleMerges)
    print('Found ' + str(len(ruleSeqs)) + ' unique executions.')
    print()
    for mr in mergedRules:
        print('Merged Rule:')
        print('============')
        print()
        print(prettyPrintRule(mr, WASM_symbols_haskell_no_coverage))
    print()
    sys.stdout.flush()
    sys.stderr.flush()
