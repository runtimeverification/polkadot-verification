#!/usr/bin/env python3

import difflib
import json
import os
import pyk
import sys
import tempfile

from pyk.kast import KApply, KConstant, KRewrite, KSequence, KToken, KVariable, _notif, _warning, _fatal

################################################################################
# Should be Upstreamed                                                         #
################################################################################

def flattenAnd(input):
    if not (pyk.isKApply(input) and input['label'] == '#And'):
        return [input]
    output = []
    work = [ arg for arg in input['args'] ]
    while len(work) > 0:
        first = work.pop(0)
        if pyk.isKApply(first) and first['label'] == '#And':
            work.extend(first['args'])
        else:
            output.append(first)
    return output

def extractTermAndConstraint(input):
    term_and_constraints = flattenAnd(input)
    term                 = [ r for r in term_and_constraints if      pyk.isKApply(r) and r['label'] == '<generatedTop>'  ][0]
    constraints          = [ r for r in term_and_constraints if not (pyk.isKApply(r) and r['label'] == '<generatedTop>') ]

    constraint = KConstant('#True')
    for c in constraints:
        constraint = KApply('#And', [c, constraint])
    return (term, constraint)

def prettyPrintRule(kRule, symbolTable):
    kRule['body'] = pyk.pushDownRewrites(kRule['body'])
    return pyk.prettyPrintKast(pyk.minimizeRule(kRule), symbolTable)

def kompile_definition(definition_dir, backend, main_defn_file, main_module, kompileArgs = [], teeOutput = True, kRelease = None):
    command = 'kompile'
    if kRelease is not None:
        command = kRelease + '/bin/' + command
    elif 'K_RELEASE' in os.environ:
        command = os.environ['K_RELEASE'] + '/bin/' + command
    kCommand = [ command , '--backend' , backend , '--directory' , definition_dir , '-I' , definition_dir , '--main-module' , main_module , main_defn_file ] + kompileArgs
    _notif('Running: ' + ' '.join(kCommand))
    return pyk._teeProcessStdout(kCommand, tee = teeOutput)

def getRuleById(definition, rule_id):
    for module in definition['modules']:
        for sentence in module['localSentences']:
            if pyk.isKRule(sentence) and 'att' in sentence:
                atts = sentence['att']['att']
                if 'UNIQUE_ID' in atts and atts['UNIQUE_ID'] == rule_id:
                    return sentence

def _runK2(command, definition, kArgs = [], teeOutput = True, kRelease = None):
    if kRelease is not None:
        command = kRelease + '/bin/' + command
    elif 'K_RELEASE' in os.environ:
        command = os.environ['K_RELEASE'] + '/bin/' + command
    kCommand = [ command , definition ] + kArgs
    _notif('Running: ' + ' '.join(kCommand))
    return pyk._teeProcessStdout(kCommand, tee = teeOutput)

def mergeRulesKoreExec(definition_dir, ruleList, kArgs = [], teeOutput = True, kRelease = None, symbolTable = None, definition = None):
    if symbolTable is not None and definition is not None:
        _notif('Merging rules:')
        for rule in ruleList:
            print()
            print('rule: ' + rule)
            print(prettyPrintRule(getRuleById(definition, rule), symbolTable))
            sys.stdout.flush()
    with tempfile.NamedTemporaryFile(mode = 'w') as tempf:
        tempf.write('\n'.join(ruleList))
        tempf.flush()
        sys.stdout.write('\n'.join(ruleList))
        sys.stdout.flush()
        return _runK2('kore-exec', definition_dir, kArgs = ['--merge-rules', tempf.name] + kArgs, teeOutput = teeOutput, kRelease = kRelease)

def mergeRules(definition_dir, main_defn_file, main_module, subsequence, symbolTable = None, definition = None):
    (rc, stdout, stderr) = mergeRulesKoreExec(definition_dir + '/' + main_defn_file + '-kompiled/definition.kore', subsequence, kArgs = ['--module', main_module], symbolTable = symbolTable, definition = definition)
    if rc == 0:
        with tempfile.NamedTemporaryFile(mode = 'w') as tempf:
            tempf.write(stdout)
            tempf.flush()
            (rc, stdout, stderr) = pyk.kast(definition_dir, tempf.name, kastArgs = ['--input', 'kore', '--output', 'json'])
            if rc != 0:
                print(stderr)
                _warning('Cannot merge rules!')
                return None
            merged_rule = json.loads(stdout)['term']
            (lhs_term, lhs_constraint) = extractTermAndConstraint(merged_rule['lhs'])
            (rhs_term, rhs_constraint) = extractTermAndConstraint(merged_rule['rhs'])
            gen_rule = pyk.KRule(KRewrite(lhs_term, rhs_term), requires = lhs_constraint, ensures = rhs_constraint)
            if symbolTable is not None:
                _notif('Merged rule:')
                print(prettyPrintRule(gen_rule, symbolTable))
                sys.stdout.flush()
            return gen_rule
    else:
        print(stderr)
        _warning('Cannot merge rules!')
        return None

def tryMergeRules(definition_dir, main_defn_file, main_module, rule_sequences):
    merged_rules = []
    for rule_sequence in rule_sequences:
        gen_rule = mergeRules(definition_dir, main_defn_file, main_module, rule_sequence)
        if gen_rule is not None:
            merged_rules.append(gen_rule)
    return merged_rules

################################################################################
# Load Definition Specific Stuff                                               #
################################################################################

WASM_definition_main_file = 'kwasm-polkadot-host'
WASM_definition_main_module = 'KWASM-POLKADOT-HOST'

WASM_definition_llvm_no_coverage_dir = '.build/defn/kwasm/llvm'
WASM_definition_llvm_coverage_dir    = '.build/defn/coverage/llvm'

WASM_definition_haskell_no_coverage_dir = '.build/defn/kwasm/haskell'
WASM_definition_haskell_coverage_dir    = '.build/defn/coverage/haskell'

WASM_definition_llvm_no_coverage = pyk.readKastTerm(WASM_definition_llvm_no_coverage_dir + '/' + WASM_definition_main_file + '-kompiled/compiled.json')
WASM_definition_llvm_coverage    = pyk.readKastTerm(WASM_definition_llvm_coverage_dir + '/' + WASM_definition_main_file + '-kompiled/compiled.json')

WASM_definition_haskell_no_coverage = pyk.readKastTerm(WASM_definition_haskell_no_coverage_dir + '/' + WASM_definition_main_file + '-kompiled/compiled.json')
WASM_definition_haskell_coverage    = pyk.readKastTerm(WASM_definition_haskell_coverage_dir + '/' + WASM_definition_main_file + '-kompiled/compiled.json')

WASM_symbols_llvm_no_coverage = pyk.buildSymbolTable(WASM_definition_llvm_no_coverage)
WASM_symbols_llvm_coverage    = pyk.buildSymbolTable(WASM_definition_llvm_coverage)

WASM_symbols_haskell_no_coverage = pyk.buildSymbolTable(WASM_definition_haskell_no_coverage)
WASM_symbols_haskell_coverage    = pyk.buildSymbolTable(WASM_definition_haskell_coverage)

################################################################################
# Runner Wrappers                                                              #
################################################################################

def kast(inputJson, *kastArgs):
    return pyk.kastJSON(WASM_definition_llvm_no_coverage_dir, inputJson, kastArgs = list(kastArgs))

def krun(inputJson, *krunArgs):
    return pyk.krunJSON(WASM_definition_llvm_no_coverage_dir, inputJson, krunArgs = list(krunArgs))

def findCoverageFiles(path):
    files = os.listdir(path)
    return [ path + '/' + f for f in files if f.endswith('_coverage.txt') ]

def krunCoverage(inputJson, *krunArgs):
    for f in findCoverageFiles(WASM_definition_llvm_coverage_dir + '/' + WASM_definition_main_file + '-kompiled'):
        os.remove(f)
    ret = pyk.krunJSON(WASM_definition_llvm_coverage_dir, inputJson, krunArgs = list(krunArgs))
    [ coverageFile ] = findCoverageFiles(WASM_definition_llvm_coverage_dir + '/' + WASM_definition_main_file + '-kompiled')
    return coverageFile

def kprove(inputJson, *krunArgs):
    return pyk.kproveJSON(WASM_definition_llvm_no_coverage, inputJson, kproveArgs = list(kproveArgs))

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

    fastPrinted = pyk.prettyPrintKast(initial_configuration['args'][0], WASM_symbols_llvm_no_coverage)
    _notif('fastPrinted output')
    print(fastPrinted)
