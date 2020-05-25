#!/usr/bin/env bash

set -euo pipefail

input_wat="$1" ; shift

echo '(module'
grep '^  (type'         "$input_wat"
grep '^  (import "env"' "$input_wat" | sed 's/  (import "env" \("[a-z1-9_]*"\) (func \(\$[a-z1-9_]*\) \((type [0-9]*)\)))/  (func \2 (export \1) \3 (phost . \2))/'
echo ')'
echo ''
echo '(register "env")'
