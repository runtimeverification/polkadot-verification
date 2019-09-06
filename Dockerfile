FROM runtimeverificationinc/ubuntu:bionic

RUN    apt-get update                                                       \
    && apt-get upgrade --yes                                                \
    && apt-get install --yes                                                \
        autoconf bison clang-8 cmake curl flex gcc git libboost-test-dev    \
        libclang-dev libcrypto++-dev libffi-dev libjemalloc-dev libmpfr-dev \
        libprocps-dev libprotobuf-dev libsecp256k1-dev libssl-dev libtool   \
        libyaml-dev libz3-dev lld-8 llvm-8-tools make maven netcat-openbsd  \
        opam openjdk-11-jdk pandoc pkg-config protobuf-compiler python3     \
        python-pygments python-recommonmark python-sphinx rapidjson-dev     \
        time z3 zlib1g-dev

ADD deps/wasm-semantics/deps/k/haskell-backend/src/main/native/haskell-backend/scripts/install-stack.sh /.install-stack/
RUN /.install-stack/install-stack.sh

USER user:user

ADD deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/bin/k-configure-opam-dev deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/bin/k-configure-opam-common /home/user/.tmp-opam/bin/
ADD deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/lib/opam  /home/user/.tmp-opam/lib/opam/
RUN    cd /home/user \
    && ./.tmp-opam/bin/k-configure-opam-dev

ADD --chown=user:user deps/wasm-semantics/deps/k/haskell-backend/src/main/native/haskell-backend/stack.yaml /home/user/.tmp-haskell/
ADD --chown=user:user deps/wasm-semantics/deps/k/haskell-backend/src/main/native/haskell-backend/kore/package.yaml /home/user/.tmp-haskell/kore/
RUN    cd /home/user/.tmp-haskell \
    && stack build --only-snapshot

RUN    cd /home/user                                                                 \
    && git clone --recursive 'https://github.com/WebAssembly/wabt' --branch='1.0.10' \
    && cd wabt                                                                       \
    && mkdir build && cd build                                                       \
    && cmake .. && cmake --build .

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PATH=/home/user/wabt/build:/home/user/.local/bin:/home/user/.cargo/bin:$PATH
