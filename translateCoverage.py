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

src_kompiled_dir = sys.argv[1]
dst_kompiled_dir = sys.argv[2]
src_rules_file   = sys.argv[3]

src_rule_map = {}
with open(src_kompiled_dir + '/allRules.txt', 'r') as src_all_rules:
    for line in src_all_rules:
        [ src_rule_hash, src_rule_loc ] = line.split(' ')
        src_rule_loc = src_rule_loc.split('/')[-1]
        src_rule_map[src_rule_hash.strip()] = src_rule_loc.strip()

dst_rule_map = {}
with open(dst_kompiled_dir + '/allRules.txt', 'r') as dst_all_rules:
    for line in dst_all_rules:
        [ dst_rule_hash, dst_rule_loc ] = line.split(' ')
        dst_rule_loc = dst_rule_loc.split('/')[-1]
        dst_rule_map[dst_rule_loc.strip()] = dst_rule_hash.strip()

src_rule_list = []
with open(src_rules_file, 'r') as src_rules:
    src_rule_list = [ rule_hash.strip() for rule_hash in src_rules ]

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

dst_rule_list = []
for src_rule in src_rule_list:
    if src_rule in src_rule_map:
        src_rule_loc = src_rule_map[src_rule]
        if src_rule_loc in dst_rule_map:
            dst_rule = dst_rule_map[src_rule_loc]
            if dst_rule in dst_non_function_rules:
                dst_rule_list.append(dst_rule)
            else:
                _notif('Skipping functional rule: ' + dst_rule)
        else:
            _fatal('COULD NOT FIND RULE LOCATION IN dst_rule_map: ' + src_rule_loc)
    else:
        _fatal('COULD NOT FIND RULE IN src_rule_map: ' + src_rule)

for dst_rule_hash in dst_rule_list:
    sys.stdout.write(dst_rule_hash + '\n')
sys.stdout.flush()
