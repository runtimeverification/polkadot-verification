#!/usr/bin/env python3

import sys
import tempfile

#from pykWasm import *
#from pykWasm import _notif, _warning, _fatal

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

#def mergeRules(rule_sequence, definition_dir, definition, main_defn_file, main_module, symbol_table, subsequence_length = 2):
#    """Merge rules which form maximal length subsequences.
#
#    Input:
#        -   rule_sequence: total sequence of all rules to look at.
#        -   definition: JSON encoding of definition to do rule merging over.
#        -   main_defn_file: name of main definition file.
#        -   main_module: name of main module of definition.
#        -   symbol_table: unparsing symbol table for definition.
#        -   subsequence_length: how large of subsequences to attempt rule merging for.
#
#    Output: List of merged rules for maximal subsequences of the given length.
#    """
#    maximal_subsequences = maximal_nonoverlapping_subsequences(rule_sequence, subsequence_length = subsequence_length)
#
#    merged_rules = []
#    for subsequence in maximal_subsequences:
#        _notif('Merging rules: ' + str(subsequence))
#        for rule_id in subsequence:
#            print('rule_id: ' + rule_id)
#            rule = getRuleById(definition, rule_id)
#            print(pyk.prettyPrintKast(rule, symbol_table))
#            print()
#
#        (rc, stdout, stderr) = mergeRulesKoreExec(definition_dir + '/' + main_defn_file + '-kompiled/definition.kore', subsequence, kArgs = ['--module', main_module])
#        if rc == 0:
#            with tempfile.NamedTemporaryFile(mode = 'w') as tempf:
#                tempf.write(stdout)
#                tempf.flush()
#                (_, stdout, stderr) = pyk.kast(definition_dir, tempf.name, kastArgs = ['--input', 'kore', '--output', 'json'])
#                merged_rule = json.loads(stdout)['term']
#                rule_pattern = KRewrite(KApply('#And', [KVariable('#CONSTRAINT'), KVariable('#INITTERM')]), KVariable('#FINALTERM'))
#                rule_subst = pyk.match(rule_pattern, merged_rule)
#                rule_body = pyk.KRewrite(rule_subst['#INITTERM'], rule_subst['#FINALTERM'])
#                gen_rule = pyk.KRule(rule_body, requires = rule_subst['#CONSTRAINT'])
#                merged_rules.append(gen_rule)
#                print(pyk.prettyPrintKast(gen_rule, WASM_symbols_haskell_no_coverage))
#                sys.stdout.flush()
#        else:
#            print(stderr)
#            _warning('Cannot merge rules!')
#
#    return merged_rules

def rule_seq_follow_count(rule_seq, rule_traces):
    rule_follow = { }
    len_seq = len(rule_seq)
    for rule_trace in rule_traces:
        for i in range(len(rule_trace) - len_seq):
            if rule_trace[i:i + len_seq] == rule_seq:
                next_rule = rule_trace[i + len_seq]
                if next_rule not in rule_follow:
                    rule_follow[next_rule] = 1
                else:
                    rule_follow[next_rule] = rule_follow[next_rule] + 1
    return rule_follow

def rule_pair_freqs(rule_traces):
    rule_seqs = { }
    for rule_trace in rule_traces:
        for new_rule in zip(rule_trace[:-1], rule_trace[1:]):
            if new_rule in rule_seqs:
                rule_seqs[new_rule] = rule_seqs[new_rule] + 1
            else:
                rule_seqs[new_rule] = 1
    return rule_seqs

def productivity_metric(num_occurances, num_occurances_init, total_rules):
    merged_success_rate = float(num_occurances) / float(num_occurances_init)
    occurance_rate      = float(num_occurances_init) / float(total_rules)
    return (merged_success_rate, occurance_rate)

def calculate_next_rule_merge(rule_traces, min_merged_success_rate = 0.25, min_occurance_rate = 0.05):
    rule_set = set([ rule for rule_trace in rule_traces for rule in rule_trace ])
    rule_occurances = { rule : 0 for rule in rule_set }
    for rule_trace in rule_traces:
        for rule in rule_trace:
            rule_occurances[rule] = rule_occurances[rule] + 1
    total_rules = sum([ rule_occurances[rule] for rule in rule_set ])
    rule_pairs = rule_pair_freqs(rule_traces)
    rules_to_merge = None
    fin_occurance_rate      = 0.0
    max_merged_success_rate = 0.0
    for rule_pair in rule_pairs.keys():
        rule_init = rule_pair[0]
        (merged_success_rate, occurance_rate) = productivity_metric(rule_pairs[rule_pair], rule_occurances[rule_init], total_rules)
        if occurance_rate > min_occurance_rate and merged_success_rate > min_merged_success_rate:
            if merged_success_rate > max_merged_success_rate:
                rules_to_merge = rule_pair
                max_merged_success_rate = merged_success_rate
                fin_occurance_rate = occurance_rate
    return (rules_to_merge, max_merged_success_rate, fin_occurance_rate)

def calculate_new_traces(rule_traces, rules_to_merge):
    new_rule = '|'.join(rules_to_merge)
    new_traces = []
    for rule_trace in rule_traces:
        new_traces.append([])
        i = 0
        while i < len(rule_trace):
            if i < len(rule_trace) - 1 and rules_to_merge == (rule_trace[i], rule_trace[i+1]):
                new_traces[-1].append(new_rule)
                i += 2
            else:
                new_traces[-1].append(rule_trace[i])
                i += 1
    return new_traces

################################################################################
# Main functionality                                                           #
################################################################################

if __name__ == '__main__':
    rule_file_paths = [ 'coverage-data/table.wast.coverage-haskell'
                      , 'coverage-data/conversion.wast.coverage-haskell'
                      , 'coverage-data/imports.wast.coverage-haskell'
                      , 'coverage-data/variables.wast.coverage-haskell'
                      , 'coverage-data/branching.wast.coverage-haskell'
                      , 'coverage-data/modules.wast.coverage-haskell'
                      , 'coverage-data/data.wast.coverage-haskell'
                      , 'coverage-data/unicode.wast.coverage-haskell'
                      , 'coverage-data/start.wast.coverage-haskell'
                      , 'coverage-data/address-c.wast.coverage-haskell'
                      , 'coverage-data/comments.wast.coverage-haskell'
                      , 'coverage-data/integers.wast.coverage-haskell'
                      , 'coverage-data/identifiers.wast.coverage-haskell'
                      ]

    rule_traces = []
    rule_sets = [set([])]
    for rule_file_path in rule_file_paths:
        with open(rule_file_path, 'r') as rule_file:
            rules = [ line.strip() for line in rule_file ]
            rule_traces.append(rules)
            rule_sets[0] = rule_sets[0].union(set(rules))
    rule_sets.append(set([]))

    # rule_traces = rule_traces[0:1]
    print(rule_traces)

    while True:
        (next_rule_merge, m1, m2) = calculate_next_rule_merge(rule_traces)
        if next_rule_merge is None:
            break
        print('Merging: ' + str(next_rule_merge) + ' with merged success rate: ' + str(m1) + ' and occurance rate: ' + str(m2))
        rule_traces = calculate_new_traces(rule_traces, next_rule_merge)
    print(rule_traces)

    sys.exit(1)


    r1 = '8c5037076555451c7425967181bb86d68c45a908dcb663cbd7265b43b08e1bce'
    r2 = 'cf4162273f4cd02153ce127e0f7f062c40fedf05a6d80709dc5412fc6bdcc494'
    rule_follow_exp = rule_seq_follow_count([r1], rule_traces)
    print(rule_follow_exp)
    print(rule_follow_exp[r2])

    rule_count1 = sum([ rule_follow_exp[k] for k in rule_follow_exp.keys() ])
    print(rule_count1)

    rule_count2 = 0
    for rule_trace in rule_traces:
        if rule_trace[-1] == r1:
            rule_count2 += 1
    print(rule_count2)

    rule_occurances = { rule : 0 for rule in rule_sets[0] }
    for rule_trace in rule_traces:
        for rule in rule_trace:
            rule_occurances[rule] = rule_occurances[rule] + 1
    print(rule_occurances)

    print(rule_pairs)

    print(rules_to_merge)
    print(max_productivity)

    #mergeRules(rules, WASM_definition_haskell_no_coverage_dir, WASM_definition_haskell_no_coverage, 'wasm-with-k-term', 'WASM-WITH-K-TERM', WASM_symbols_haskell_no_coverage, subsequence_length = subsequence_length)
