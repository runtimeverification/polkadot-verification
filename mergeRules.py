#!/usr/bin/env python3

import sys
import tempfile

from pykWasm import *
from pykWasm import _notif, _warning, _fatal

################################################################################
# Rule Merging based on maximal non-overlapping subsequences                   #
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

def merge_rules_max_subsequences(definition_dir, main_defn_file, main_module, rule_sequences, subsequence_length = 2):
    """Merge rules which form maximal length subsequences.

    Input:
        -   definition_dir: directory of definition to do rule merging in.
        -   main_defn_file: name of main definition file.
        -   main_module: name of main module of definition.
        -   rule_sequences: total sequence of all rules to look at.
        -   subsequence_length: how large of subsequences to attempt rule merging for.

    Output: List of merged rules for maximal subsequences of the given length.
    """
    maximal_subsequences = []
    for rule_sequence in rule_sequences:
        maximal_subsequences.extend(maximal_nonoverlapping_subsequences(rule_sequence, subsequence_length = subsequence_length))
    return tryMergeRules(definition_dir, main_defn_file, main_module, maximal_subsequences)

################################################################################
# Merging rules based on max productivity                                      #
################################################################################

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

def merge_rules_max_productivity(definition_dir, main_defn_file, main_module, rule_sequences, min_merged_success_rate = 0.25, min_occurance_rate = 0.05):
    """Merge rules which will cause maximal productivity for a given backend.

    Input:
        -   definition_dir: Directory where definition lives.
        -   main_defn_file: name of main definition file.
        -   main_module: name of main module of definition.
        -   rule_sequences: all sequences to use as input data for deciding productivity.
        -   min_merged_success_rate: how often the resulting merged rule should apply (relative to how many times the first step in the rule would have applied).
        -   min_occurance_rate: how often the first step in the merged rule should apply relative to all the rules.

    Output: List of merged rules to add to definition at lower priority.
    """

    while True:
        (next_rule_merge, m1, m2) = calculate_next_rule_merge(rule_sequences)
        if next_rule_merge is None:
            break
        print('Merging: ' + str(next_rule_merge) + ' with merged success rate: ' + str(m1) + ' and occurance rate: ' + str(m2))
        sys.stdout.flush()
        rule_sequences = calculate_new_traces(rule_sequences, next_rule_merge)
    merged_rule_traces = set([])
    for rule_sequence in rule_sequences:
        for rule in rule_sequence:
            if len(rule.split('|')) > 1:
                merged_rule_traces.add(rule)
    merge_rules = [ rule.split('|') for rule in merged_rule_traces ]
    return tryMergeRules(definition_dir, main_defn_file, main_module, merge_rules)

################################################################################
# Main functionality                                                           #
################################################################################

if __name__ == '__main__':
    merge_type  = sys.argv[1]
    merge_files = sys.argv[2:]

    rule_traces = []
    for rule_file_path in merge_files:
        with open(rule_file_path, 'r') as rule_file:
            rules = [ line.strip() for line in rule_file ]
            rule_traces.append(rules)

    if merge_type == 'direct':
        merged_rules = tryMergeRules(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, rule_traces)
    elif merge_type == 'max-subseq':
        merged_rules = merge_rules_max_subsequences(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, rule_traces, subsequence_length = 2)
    elif merge_type == 'max-productivity':
        merged_rules = merge_rules_max_productivity(WASM_definition_haskell_no_coverage_dir, WASM_definition_main_file, WASM_definition_main_module, rule_traces, min_merged_success_rate = 0.25, min_occurance_rate = 0.05)
    else:
        _fatal('Unknown merge technique: ' + merge_type)

    _notif('Merged rules!')
    for merged_rule in merged_rules:
        print()
        print(pyk.prettyPrintKast(merged_rule, WASM_symbols_haskell_no_coverage))
        sys.stdout.flush()
