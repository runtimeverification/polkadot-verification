#!/usr/bin/env bash

# Currently we are importing K-TERM as a hack to get around various unparsing issues when using `pyk` library.
# K-TERM defines three separate productions with the same KLabel/Symbol for `#EmptyK`, and two separate ones for `#EmptyKList`.
# The Haskell backend rejects definitions which have multiple definitions of the same symbol, so this causes it to crash.
# This file forcibly strips all but one of the occurances of each label from the resulting `definition.kore`.

set -euo pipefail

input_definition="$1" && shift

lines=( $(grep --line-number "symbol Lbl'Hash'EmptyK{}() :"     "$input_definition" | cut --delimiter=':' --field=1 | tail -n +2))
lines+=($(grep --line-number "symbol Lbl'Hash'EmptyKList{}() :" "$input_definition" | cut --delimiter=':' --field=1 | tail -n +2))

sed_command=''

for line in ${lines[@]}; do
    sed_command="${sed_command}${line}d;"
done

sed -i "$sed_command" "$input_definition"
