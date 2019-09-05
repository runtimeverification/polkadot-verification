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
                                 ]

for symb in WASM_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM', symb)

WASM_TEST_underbar_unparsed_symbols = [ '(register_)_WASM-TEST__WasmString'
                                      ]

for symb in WASM_TEST_underbar_unparsed_symbols:
    WASM_symbols[symb] = underbarUnparsingInModule('WASM-TEST', symb)

ALL_symbols = pyk.combineDicts(pyk.K_symbols, WASM_symbols)

def kast(inputJson, *kastArgs):
    return pyk.kastJSON('.build/defn/llvm', inputJson, kastArgs = list(kastArgs), kRelease = 'deps/k/k-distribution/target/release/k')

def krun(inputJson, *krunArgs):
    return pyk.krunJSON('.build/defn/llvm', inputJson, krunArgs = list(krunArgs), kRelease = 'deps/k/k-distribution/target/release/k')

def kprove(inputJson, *krunArgs):
    return pyk.kproveJSON('.build/defn/llvm', inputJson, kproveArgs = list(kproveArgs), kRelease = 'deps/k/k-distribution/target/release/k')

moduleInst = KApply( '<moduleInst>' , [ KApply( '<modIdx>'      , [ KVariable('MODIDX_CELL')      ])
                                      , KApply( '<exports>'     , [ KVariable('EXPORTS_CELL')     ])
                                      , KApply( '<typeIds>'     , [ KVariable('TYPEIDS_CELL')     ])
                                      , KApply( '<types>'       , [ KVariable('TYPES_CELL')       ])
                                      , KApply( '<nextTypeIdx>' , [ KVariable('NEXTTYPEIDX_CELL') ])
                                      , KApply( '<funcIds>'     , [ KVariable('FUNCIDS_CELL')     ])
                                      , KApply( '<funcAddrs>'   , [ KVariable('FUNCADDRS_CELL')   ])
                                      , KApply( '<nextFuncIdx>' , [ KVariable('NEXTFUNCIDX_CELL') ])
                                      , KApply( '<tabIds>'      , [ KVariable('TABIDS_CELL')      ])
                                      , KApply( '<tabAddrs>'    , [ KVariable('TABADDRS_CELL')    ])
                                      , KApply( '<memIds>'      , [ KVariable('MEMIDS_CELL')      ])
                                      , KApply( '<memAddrs>'    , [ KVariable('MEMADDRS_CELL')    ])
                                      , KApply( '<globIds>'     , [ KVariable('GLOBIDS_CELL')     ])
                                      , KApply( '<globalAddrs>' , [ KVariable('GLOBALADDRS_CELL') ])
                                      , KApply( '<nextGlobIdx>' , [ KVariable('NEXTGLOBIDX_CELL') ])
                                      ]
                   )

funcDef =  KApply( '<funcDef>' , [ KApply( '<fAddr>'    , [ KVariable('FADDR_CELL')    ])
                                 , KApply( '<fCode>'    , [ KVariable('FCODE_CELL')    ])
                                 , KApply( '<fType>'    , [ KVariable('FTYPE_CELL')    ])
                                 , KApply( '<fLocal>'   , [ KVariable('FLOCAL_CELL')   ])
                                 , KApply( '<fModInst>' , [ KVariable('FMODINST_CELL') ])
                                 ]
                 )

tabInst = KApply ( '<tabInst>' , [ KApply( '<tAddr>' , [ KVariable('TADDR_CELL') ])
                                 , KApply( '<tmax>'  , [ KVariable('TMAX_CELL')  ])
                                 , KApply( '<tsize>' , [ KVariable('TSIZE_CELL') ])
                                 , KApply( '<tdata>' , [ KVariable('TDATA_CELL') ])
                                 ]
                 )

memInst = KApply( 'memInst' , [ KApply( '<mAddr>' , [ KVariable('MADDR_CELL') ])
                              , KApply( '<mmax>'  , [ KVariable('MMAX_CELL')  ])
                              , KApply( '<msize>' , [ KVariable('MSIZE_CELL') ])
                              , KApply( '<mdata>' , [ KVariable('MDATA_CELL') ])
                              ]
                )

globalInst = KApply( '<globalInst>' , [ KApply( '<gAddr>'  , [ KVariable('GADDR_CELL')  ])
                                      , KApply( '<gValue>' , [ KVariable('GVALUE_CELL') ])
                                      , KApply( '<gMut>'   , [ KVariable('GMUT_CELL')   ])
                                      ]
                   )

wasm = KApply( '<wasm>' , [ KApply( '<k>'              , [ KVariable('K_CELL') ])
                          , KApply( '<valstack>'       , [ KVariable('VALSTACK_CELL') ])
                          , KApply( '<curFrame>'       , [ KApply( '<locals>'     , [ KVariable('LOCALS_CELL')     ])
                                                         , KApply( '<localIds>'   , [ KVariable('LOCALIDS_CELL')   ])
                                                         , KApply( '<curModIdx>'  , [ KVariable('CURMODIDX_CELL')  ])
                                                         , KApply( '<labelDepth>' , [ KVariable('LABELDEPTH_CELL') ])
                                                         , KApply( '<labelIds>'   , [ KVariable('LABELIDS_CELL')   ])
                                                         ]
                                  )
                          , KApply( '<moduleRegistry>'  , [ KVariable('MODULEREGISTRY_CELL')  ])
                          , KApply( '<moduleIds>'       , [ KVariable('MODULEIDS_CELL')       ])
                          , KApply( '<moduleInstances>' , [ KVariable('MODULEINSTANCES_CELL') ]) # Map{moduleInst}
                          , KApply( '<nextModuleIdx>'   , [ KVariable('NEXTMODULEIDX_CELL')   ])
                          , KApply( '<mainStore>' , [ KApply( '<funcs>'        , [ KVariable('FUNCS_CELL')        ]) # Map{funcDef}
                                                    , KApply( '<nextFuncAddr>' , [ KVariable('NEXTFUNCADDR_CELL') ])
                                                    , KApply( '<tabs>'         , [ KVariable('TABS_CELL')         ]) # Map{tabInst}
                                                    , KApply( '<nextTabAddr>'  , [ KVariable('NEXTTABADDR_CELL')  ])
                                                    , KApply( '<mems>'         , [ KVariable('MEMS_CELL')         ]) # Map{memInst}
                                                    , KApply( '<nextMemAddr>'  , [ KVariable('NEXTMEMADDR_CELL')  ])
                                                    , KApply( '<globals>'      , [ KVariable('GLOBALS_CELL')      ]) # Map{globalInst}
                                                    , KApply( '<nextGlobAddr>' , [ KVariable('NEXTGLOBADDR_CELL') ])
                                                    ]
                                  )
                          , KApply( '<deterministicMemoryGrowth>' , [ KVariable('DETERMINISTICMEMORYGROWTH_CELL') ])
                          , KApply( '<nextFreshId>'               , [ KVariable('NEXTFRESHID_CELL')               ])
                          ]
             )

generatedTop = KApply( '<generatedTop>' , [ wasm
                                          , KApply( '<generatedCounter>' , [ KVariable('GENERATEDCOUNTER_CELL') ])
                                          ]
                     )

initSubst = { 'K_CELL'                         : KSequence([KConstant('.List{"___WASM__Stmt_Stmts"}_Stmts')]) # retrieved from kore_to_k_labels.properties
            , 'VALSTACK_CELL'                  : KConstant('.ValStack_WASM-DATA_')
            , 'LOCALS_CELL'                    : KConstant('.Map')
            , 'LOCALIDS_CELL'                  : KConstant('.Map')
            , 'CURMODIDX_CELL'                 : KConstant('.Int_WASM-DATA_')
            , 'LABELDEPTH_CELL'                : KToken('0', 'Int')
            , 'LABELIDS_CELL'                  : KConstant('.Map')
            , 'MODULEREGISTRY_CELL'            : KConstant('.Map')
            , 'MODULEIDS_CELL'                 : KConstant('.Map')
            , 'MODULEINSTANCES_CELL'           : KConstant('.ModuleInstCellMap')
            , 'NEXTMODULEIDX_CELL'             : KToken('0', 'Int')
            , 'FUNCS_CELL'                     : KConstant('.FuncDefCellMap')
            , 'NEXTFUNCADDR_CELL'              : KToken('0', 'Int')
            , 'TABS_CELL'                      : KConstant('.TabInstCellMap')
            , 'NEXTTABADDR_CELL'               : KToken('0', 'Int')
            , 'MEMS_CELL'                      : KConstant('.MemInstCellMap')
            , 'NEXTMEMADDR_CELL'               : KToken('0', 'Int')
            , 'GLOBALS_CELL'                   : KConstant('.GlobalInstCellMap')
            , 'NEXTGLOBADDR_CELL'              : KToken('0', 'Int')
            , 'DETERMINISTICMEMORYGROWTH_CELL' : KToken('true', 'Bool')
            , 'NEXTFRESHID_CELL'               : KToken('0', 'Int')
            , 'GENERATEDCOUNTER_CELL'          : KToken('0', 'Int')
            }

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

