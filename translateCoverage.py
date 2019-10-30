#!/usr/bin/env python3

import json
import sys

from pykWasm import *

def _notif(msg):
    sys.stderr.write('=== ' + msg + '\n')
    sys.stderr.flush()

def _fatal(msg, exit_code = 1):
    sys.stderr.write('!!! ' + msg + '\n')
    sys.stderr.flush()
    sys.exit(exit_code)

def translateCoverage(src_all_rules, dst_all_rules, dst_definition, src_rules_list):
    """Translate the coverage data from one kompiled definition to another.

    Input:

        -   src_all_rules: contents of allRules.txt for definition which coverage was generated for.
        -   dst_all_rules: contents of allRules.txt for definition which you desire coverage for.
        -   dst_definition: JSON encoded definition of dst kompiled definition.
        -   src_rules_list: Actual coverage data produced.

    Output: list of non-functional rules applied in dst definition translated from src definition.
    """

    # Load the src_rule_id -> src_source_location rule map from the src kompiled directory
    src_rule_map = {}
    for line in src_all_rules:
        [ src_rule_hash, src_rule_loc ] = line.split(' ')
        src_rule_loc = src_rule_loc.split('/')[-1]
        src_rule_map[src_rule_hash.strip()] = src_rule_loc.strip()

    # Load the dst_rule_id -> dst_source_location rule map (and inverts it) from the dst kompiled directory
    dst_rule_map = {}
    for line in dst_all_rules:
        [ dst_rule_hash, dst_rule_loc ] = line.split(' ')
        dst_rule_loc = dst_rule_loc.split('/')[-1]
        dst_rule_map[dst_rule_loc.strip()] = dst_rule_hash.strip()

    src_rule_list = [ rule_hash.strip() for rule_hash in src_rules_list ]

    # Filter out non-functional rules from rule map (determining if they are functional via the top symbol in the rule being `<generatedTop>`)
    dst_non_function_rules = []
    dst_kompiled = pyk.readKastTerm(dst_kompiled_dir + '/compiled.json')
    for module in dst_kompiled['modules']:
        for sentence in module['localSentences']:
            if pyk.isKRule(sentence):
                ruleBody = sentence['body']
                ruleAtt  = sentence['att']['att']
                if    (pyk.isKApply(ruleBody)                                     and ruleBody['label']        == '<generatedTop>') \
                   or (pyk.isKRewrite(ruleBody) and pyk.isKApply(ruleBody['lhs']) and ruleBody['lhs']['label'] == '<generatedTop>'):
                    if 'UNIQUE_ID' in ruleAtt:
                        dst_non_function_rules.append(ruleAtt['UNIQUE_ID'])

    # Convert the src_coverage rules to dst_no_coverage rules via the maps generated above
    dst_rule_list = []
    for src_rule in src_rule_list:
        if src_rule in src_rule_map:
            src_rule_loc = src_rule_map[src_rule]
            if src_rule_loc in dst_rule_map:
                dst_rule = dst_rule_map[src_rule_loc]
                if dst_rule in dst_non_function_rules:
                    dst_rule_list.append(dst_rule)
                else:
                    _notif('Skipping non-semantic rule: ' + dst_rule)
            else:
                _fatal('COULD NOT FIND RULE LOCATION IN dst_rule_map: ' + src_rule_loc)
        else:
            _fatal('COULD NOT FIND RULE IN src_rule_map: ' + src_rule)

    return dst_rule_list

def translateCoverageFromPaths(src_komplied_dir, dst_kompiled_dir, src_rules_file):
    """Translate coverage information given paths to needed files.

    Input:

        -   src_kompiled_dir: Path to *-kompiled directory of source.
        -   dst_kompiled_dir: Path to *-kompiled directory of destination.
        -   src_rules_file: Path to generated rules coverage file.

    Output: Translated list of rules with non-semantic rules stripped out.
    """
    src_all_rules = []
    with open(src_kompiled_dir + '/allRules.txt', 'r') as src_all_rules_file:
        src_all_rules = [ line.strip() for line in src_all_rules_file ]

    dst_all_rules = []
    with open(dst_kompiled_dir + '/allRules.txt', 'r') as dst_all_rules_file:
        dst_all_rules = [ line.strip() for line in dst_all_rules_file ]

    dst_definition = pyk.readKastTerm(dst_kompiled_dir + '/compiled.json')

    src_rules_list = []
    with open(src_rules_file, 'r') as src_rules:
        src_rules_list = [ line.strip() for line in src_rules ]

    return translateCoverage(src_all_rules, dst_all_rules, dst_definition, src_rules_list)

if __name__ == '__main__':
    src_kompiled_dir = sys.argv[1]  # usually .build/defn/coverage/llvm/wasm-with-k-io-kompiled
    dst_kompiled_dir = sys.argv[2]  # usually .build/defn/kwasm/haskell/wasm-with-k-io-kompiled
    src_rules_file   = sys.argv[3]  # usually something like deps/wasm-semantics/tests/simple/constants.wast.llvm-coverage

    dst_rules_list = translateCoverageFromPaths(src_kompiled_dir, dst_kompiled_dir, src_rules_file)

    # Print the new rule list one line at a time.
    sys.stdout.write('\n'.join(dst_rules_list) + '\n')
    sys.stdout.flush()
