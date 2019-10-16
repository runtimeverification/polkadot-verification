#!/usr/bin/env python3

import sys
import tempfile

from pykWasm import *
from pykWasm import _notif, _warning, _fatal

################################################################################
# Calculate subsequences and find the maximal subsequences                     #
################################################################################

def maximal_nonoverlapping_subsequences(sequence, subsequence_length = 2):
    """Calculate maximal length non-overlapping subsequences from a given sequence of strings.

    Input:

        -   sequence: list of strings.
        -   subsequence_length: size of subsequences to look for.

    Output: maximal non-overlapping subsequences, with earlier subsequences preferred.
    """
    subsequences = { }

    for i in range(0, len(sequence) - subsequence_length):
        subsequence = '|'.join(sequence[ i : i + subsequence_length ])
        if subsequence in subsequences:
            subsequences[subsequence] += 1
        else:
            subsequences[subsequence] = 1

    maximal_subsequences          = []
    maximal_subsequence_count     = 0
    maximal_subsequences_rule_set = set([])

    for subsequence in subsequences.keys():
        rule_set = set(subsequence.split('|'))
        if subsequences[subsequence] > maximal_subsequence_count:
            maximal_subsequences          = [subsequence]
            maximal_subsequence_count     = subsequences[subsequence]
            maximal_subsequences_rule_set = rule_set
        elif subsequences[subsequence] == maximal_subsequence_count:
            if not any([ rule in maximal_subsequences_rule_set for rule in rule_set ]):
                maximal_subsequences.append(subsequence)
                maximal_subsequences_rule_set = maximal_subsequences_rule_set.union(rule_set)

    return [ subsequence.split('|') for subsequence in maximal_subsequences ]

################################################################################
# Generate merged rules for selected maximal subsequences                      #
################################################################################

def mergeRules(rule_sequence, definition_dir, definition, main_defn_file, main_module, symbol_table, subsequence_length = 2):
    """Merge rules which form maximal length subsequences.

    Input:
        -   rule_sequence: total sequence of all rules to look at.
        -   definition: JSON encoding of definition to do rule merging over.
        -   main_defn_file: name of main definition file.
        -   main_module: name of main module of definition.
        -   symbol_table: unparsing symbol table for definition.
        -   subsequence_length: how large of subsequences to attempt rule merging for.

    Output: List of merged rules for maximal subsequences of the given length.
    """
    maximal_subsequences = maximal_nonoverlapping_subsequences(rule_sequence, subsequence_length = subsequence_length)

    merged_rules = []
    for subsequence in maximal_subsequences:
        _notif('Merging rules: ' + str(subsequence))
        for rule_id in subsequence:
            print('rule_id: ' + rule_id)
            rule = getRuleById(definition, rule_id)
            print(pyk.prettyPrintKast(rule, symbol_table))
            print()

        (rc, stdout, stderr) = mergeRulesKoreExec(definition_dir + '/' + main_defn_file + '-kompiled/definition.kore', subsequence, kArgs = ['--module', main_module])
        if rc == 0:
            with tempfile.NamedTemporaryFile(mode = 'w') as tempf:
                tempf.write(stdout)
                tempf.flush()
                (_, stdout, stderr) = pyk.kast(definition_dir, tempf.name, kastArgs = ['--input', 'kore', '--output', 'json'])
                merged_rule = json.loads(stdout)['term']
                rule_pattern = KRewrite(KApply('#And', [KVariable('#CONSTRAINT'), KVariable('#INITTERM')]), KVariable('#FINALTERM'))
                rule_subst = pyk.match(rule_pattern, merged_rule)
                rule_body = pyk.KRewrite(rule_subst['#INITTERM'], rule_subst['#FINALTERM'])
                gen_rule = pyk.KRule(rule_body, requires = rule_subst['#CONSTRAINT'])
                merged_rules.append(gen_rule)
                print(pyk.prettyPrintKast(gen_rule, WASM_symbols_haskell_no_coverage))
                sys.stdout.flush()
        else:
            print(stderr)
            _warning('Cannot merge rules!')

    return merged_rules

################################################################################
# Main functionality                                                           #
################################################################################

if __name__ == '__main__':
    rules_file_path    = sys.argv[1]
    subsequence_length = int(sys.argv[2])

    rules = []
    with open(rules_file_path, 'r') as rules_file:
        rules = [ line.strip() for line in rules_file ]

    mergeRules(rules, WASM_definition_haskell_no_coverage_dir, WASM_definition_haskell_no_coverage, 'wasm-with-k-term', 'WASM-WITH-K-TERM', WASM_symbols_haskell_no_coverage, subsequence_length = subsequence_length)
