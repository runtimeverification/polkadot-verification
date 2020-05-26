#!/usr/bin/env bash
# This script reads in a Pwasm module and tries to automatically construct a module that models all the host functions.
# It does so by extracting all types and all function imports from the `"env"` input module and declaring corresponding functions in the new module.
# The process relies on each type and import being declared on a separate, single line.
set -euo pipefail

input_wat="$1" ; shift

echo '(module'
grep '^  (type'         "$input_wat"
grep '^  (import "env"' "$input_wat" | sed 's/  (import "env" \("[a-z1-9_]*"\) (func \(\$[a-z1-9_]*\) \((type [0-9]*)\)))/  (func \2 (export \1) \3 (phost . \2))/'
echo ')'
echo ''
echo '(register "env")'
