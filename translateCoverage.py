#!/usr/bin/env python3

import json
import sys

from pykWasm      import *
from pyk.coverage import *

if __name__ == '__main__':
    src_kompiled_dir = sys.argv[1]  # usually .build/defn/coverage/llvm/kwasm-pre-kompiled
    dst_kompiled_dir = sys.argv[2]  # usually .build/defn/kwasm/haskell/kwasm-pre-kompiled
    src_rules_file   = sys.argv[3]  # usually something like deps/wasm-semantics/tests/simple/constants.wast.llvm-coverage

    dst_rules_list = translateCoverageFromPaths(src_kompiled_dir, dst_kompiled_dir, src_rules_file)

    # Print the new rule list one line at a time.
    sys.stdout.write('\n'.join(dst_rules_list) + '\n')
    sys.stdout.flush()
