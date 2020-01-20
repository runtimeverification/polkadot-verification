#!/usr/bin/env python3

import pyk
import random
import sys
from pykWasm import *
from pykWasm import _fatal, _notif, _warning

sys.setrecursionlimit(150000000)

kastProgram = pyk.readKastTerm('src/polkadot-runtime.wat.json')

function_name = '$srml_balances::Module<T_I>::set_free_balance::h740a36cc4860a8fe'

wasm_invoke = lambda fid: KApply('(invoke_)_WASM__Int', [KToken(str(fid), 'Int')])
wasm_push = lambda type, value: KApply('(_)_WASM-TEXT__PlainInstr', [KApply('_.const__WASM__IValType_Int', [KApply(type + '_WASM-DATA_', []), value])])

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

(symbolic_config, init_subst) = get_init_config()

init_stmts = wasm_stmts_flattened(kastProgram)

invoking_steps = init_stmts                          \
               + [ wasm_push('i32', KVariable('V1'))
                 , wasm_push('i64', KVariable('V2'))
                 , wasm_push('i64', KVariable('V3'))
                 , wasm_invoke(156)
                 ]

init_subst['K_CELL'] = wasm_stmts(invoking_steps)

init_config = pyk.substitute(symbolic_config, init_subst)

invokingSubstitution = { 'V1' : KToken(str(random.randint(0, 2 ** 32)), 'Int')
                       , 'V2' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                       , 'V3' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                       }

init_config = pyk.substitute(init_config, invokingSubstitution)

print(init_config)
print(pyk.prettyPrintKast(init_config, WASM_symbols_llvm_no_coverage))
(_, after_running, _) = krun({ 'format' : 'KAST' , 'version': 1, 'term': init_config })
print(pyk.prettyPrintKast(after_running, WASM_symbols_llvm_no_coverage))
sys.stdout.flush()
