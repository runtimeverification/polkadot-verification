#!/usr/bin/env python3

import pyk
import random
import sys
import time

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
                 , wasm_call(function_name)
                 ]

numExec = int(sys.argv[1])
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

[ ruleSeq ] = [ ruleSeq.split('|') for ruleSeq in ruleSeqs ]

#checkRuleSeqs = [ ruleSeq[114:144] # 10.876354694366455
#                , ruleSeq[203:233] # 10.688526630401611
#                , ruleSeq[266:296] # 11.039204359054565
#                , ruleSeq[355:385] # 13.242290735244751
#                ]
#mergedRules = tryMergeRules(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, checkRuleSeqs)
#for mr in mergedRules:
#    print('Merged Rule:')
#    print('============')
#    print(prettyPrintRule(mr, WASM_symbols_haskell_no_coverage))
#    print()
#    sys.stdout.flush()

merge_length = 30
merge_step = 1
ruleSeqs0 = [ (i, i+merge_length) for i in range(0,len(ruleSeq) - merge_length,merge_step) ]
ruleSeqs = ruleSeqs0 + ruleSeqs0 + ruleSeqs0
merge_stats = []
for (i, (start, end)) in enumerate(ruleSeqs):
    rS = ruleSeq[start:end]
    start_time = time.time()
    print()
    print('Trying ' + str(i) + '/' + str(len(ruleSeqs)) + ': ' + str(start) + ' - ' + str(end))
    print("==================================================================================")
    print('\n'.join(rS))
    sys.stdout.flush()
    mergedRules = tryMergeRules(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, [rS])
    if len(mergedRules) > 0:
        print('SUCCESS')
        #for mr in mergedRules:
        #    print('Merged Rule:')
        #    print('============')
        #    print()
        #    print(prettyPrintRule(mr, WASM_symbols_haskell_no_coverage))
    else:
        print('FAILURE')
    sys.stdout.flush()
    end_time = time.time()
    merge_stats.append((start, end, end_time - start_time))

sorted_merge_stats = sorted(merge_stats, key = lambda ms: ms[2])
print('\n'.join([str(sms) for sms in sorted_merge_stats]))
print()
sys.stdout.flush()

#failed_lengths  = [ 113 , 150 , 600 , 1200 ]
#success_lengths = [ 0 , 75 , 94 , 104 ]
#current_length = 109
#while current_length not in (success_lengths + failed_lengths):
#    print()
#    print('trying length: ' + str(current_length))
#    ruleSeqs = [ ruleSeq[0:current_length] ]
#    ruleMerges = ruleSeqs
#    mergedRules = tryMergeRules(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, ruleMerges)
#    print()
#    if len(mergedRules) == 1:
#        success_lengths.append(current_length)
#        print('length succeeded: ' + str(current_length))
#    else:
#        failed_lengths.insert(0, current_length)
#        print('length failed: ' + str(current_length))
#    print()
#    sys.stdout.flush()
#    current_length = int(((success_lengths[-1] + 1) + failed_lengths[0]) / 2)
#print()
#print('success_lengths: ' + str(success_lengths))
#print('failed_lengths: ' + str(failed_lengths))
#sys.stdout.flush()

#
#print('Found ' + str(len(ruleSeqs)) + ' unique executions.')
#print()
#for mr in mergedRules:
#    print('Merged Rule:')
#    print('============')
#    print()
#    print(prettyPrintRule(mr, WASM_symbols_haskell_no_coverage))
#print()
#sys.stdout.flush()
#sys.stderr.flush()
