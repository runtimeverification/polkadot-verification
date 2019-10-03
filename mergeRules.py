#!/usr/bin/env python3

import os
import sys
import tempfile

from pykWasm import *
from pykWasm import _notif, _warning, _fatal

rules = []
with open(sys.argv[1], 'r') as rule_file:
    rules = [ line.strip() for line in rule_file ]

subsequence_length = int(sys.argv[2])

################################################################################
# Should be Upstreamed                                                         #
################################################################################

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

def mergeRules(definition, ruleList, kArgs = [], teeOutput = True, kRelease = None):
    with tempfile.NamedTemporaryFile(mode = 'w') as tempf:
        tempf.write('\n'.join(ruleList))
        tempf.flush()
        sys.stdout.write('\n'.join(ruleList))
        sys.stdout.flush()
        return _runK2('kore-exec', definition, kArgs = ['--merge-rules', tempf.name] + kArgs, teeOutput = teeOutput, kRelease = kRelease)

################################################################################
# Calculate subsequences and find the maximal subsequences                     #
################################################################################

subsequences = { }

for i in range(0, len(rules) - subsequence_length):
    subsequence = '|'.join(rules[ i : i + subsequence_length ])
    if subsequence in subsequences:
        subsequences[subsequence] += 1
    else:
        subsequences[subsequence] = 1

maximal_subsequences      = []
maximal_subsequence_count = 0

for subsequence in subsequences.keys():
    if subsequences[subsequence] > maximal_subsequence_count:
        maximal_subsequences      = [subsequence]
        maximal_subsequence_count = subsequences[subsequence]
    elif subsequences[subsequence] == maximal_subsequence_count:
        maximal_subsequences.append(subsequence)

################################################################################
# Generate merged rules for selected maximal subsequences                      #
################################################################################

for subsequence in maximal_subsequences:
    _notif('Merging rules: ' + subsequence)
    rule_ids = subsequence.split('|')
    for rule_id in rule_ids:
        print('rule_id: ' + rule_id)
        rule = getRuleById(WASM_definition_haskell_no_coverage, rule_id)
        print(pyk.prettyPrintKast(rule, WASM_symbols_haskell_no_coverage))
        print()

    (rc, stdout, stderr) = mergeRules(WASM_definition_haskell_no_coverage_dir + '/wasm-with-k-term-kompiled/definition.kore', rule_ids, kArgs = ['--module', 'WASM-WITH-K-TERM'])
    if rc == 0:
        with tempfile.NamedTemporaryFile(mode = 'w') as tempf:
            tempf.write(stdout)
            tempf.flush()
            (_, stdout, stderr) = pyk.kast(WASM_definition_haskell_no_coverage_dir, tempf.name, kastArgs = ['--input', 'kore', '--output', 'json'])
            (_, stdout2, stderr2) = pyk.kast(WASM_definition_haskell_no_coverage_dir, tempf.name, kastArgs = ['--input', 'kore', '--output', 'pretty'])
            kast_output = json.loads(stdout)['term']
            # print(pyk.prettyPrintKast(kast_output, WASM_symbols_haskell_no_coverage))
            rule_pattern = KApply('#Implies', [KApply('#And', [KVariable('#CONSTRAINT'), KVariable('#INITTERM')]), KVariable('#FINALTERM')])
            rule_subst = pyk.match(rule_pattern, kast_output)
            # print(str(rule_subst))
            rule_body = pyk.KRewrite(rule_subst['#INITTERM'], rule_subst['#FINALTERM'])
            gen_rule = pyk.KRule(rule_body, requires = rule_subst['#CONSTRAINT'])
            print(pyk.prettyPrintKast(gen_rule, WASM_symbols_haskell_no_coverage))
    else:
        print(stderr)
        _warning('Cannot merge rules!')
