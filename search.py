#!/usr/bin/env python3

import pyk
import random
import sys
from pykWasm import *

sys.setrecursionlimit(150000000)

kastProgram = pyk.readKastTerm('src/polkadot-runtime.wat.json')
#loadedTerm  = pyk.readKastTerm('src/polkadot-runtime.loaded.json')

function_name = '$srml_balances::Module<T_I>::set_free_balance::h740a36cc4860a8fe'

wasm_invoke = lambda fid: KApply('(invoke_)_WASM__Int', [KToken(str(fid), 'Int')])
wasm_push = lambda type, value: KApply('(_)_WASM-TEXT__PlainInstr', [KApply('_.const__WASM__IValType_Int', [KApply(type + '_WASM-DATA_', []), value])])

def wasm_stmts(vs, stmtType = 'Stmt'):
    if len(vs) == 0:
        return KConstant('.List{"___WASM__EmptyStmt_EmptyStmts"}_EmptyStmts')
    inst  = vs[0]
    insts = vs[1:]
    return KApply('___WASM__' + stmtType + '_' + stmtType + 's', [inst, wasm_stmts(insts)])

def wasm_stmts_flattened(stmts, stmtType = 'Stmt'):
    if not pyk.isKApply(stmts):
        _fatal('Must be a KApply')
    if stmts['label'] == '___WASM__' + stmtType + '_' + stmtType + 's':
        return [ stmts['args'][0] ] + wasm_stmts_flattened(stmts['args'][1])
    elif stmts['label'] == '.List{"___WASM__EmptyStmt_EmptyStmts"}_EmptyStmts':
        return []
    else:
        _fatal('Not of type ' + stmtType + '!')

kastSteps = wasm_stmts_flattened(kastProgram)
kastSteps.append(wasm_push('i32', KVariable('V1')))
kastSteps.append(wasm_push('i64', KVariable('V2')))
kastSteps.append(wasm_push('i64', KVariable('V3')))
kastSteps.append(wasm_invoke(156))

invokedProgram = wasm_stmts(kastSteps)

invokingSubstitution = { 'V1' : KToken(str(random.randint(0, 2 ** 32)), 'Int')
                       , 'V2' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                       , 'V3' : KToken(str(random.randint(0, 2 ** 64)), 'Int')
                       }

invokedProgram = pyk.substitute(invokedProgram, invokingSubstitution)

#print(pyk.prettyPrintKast(kastProgram, ALL_symbols))
print(pyk.prettyPrintKast(invokedProgram, ALL_symbols))
#print(pyk.prettyPrintKast(loadedTerm , ALL_symbols))
