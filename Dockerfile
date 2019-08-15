FROM runtimeverificationinc/ubuntu:bionic

RUN    apt-get update                                                  \
    && apt-get upgrade --yes                                           \
    && apt-get install --yes                                           \
        autoconf clang cmake curl flex gcc git libclang-dev libffi-dev \
        libmpfr-dev libssl-dev libtool libz3-dev make maven opam       \
        openjdk-11-jdk pandoc pkg-config python3 python-pygments       \
        python-recommonmark python-sphinx time z3 zlib1g-dev

ADD deps/wasm-semantics/deps/k/haskell-backend/src/main/native/haskell-backend/scripts/install-stack.sh /.install-stack/
RUN /.install-stack/install-stack.sh

USER user:user

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain 1.28.0

ADD deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/bin/k-configure-opam-dev deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/bin/k-configure-opam-common /home/user/.tmp-opam/bin/
ADD deps/wasm-semantics/deps/k/k-distribution/src/main/scripts/lib/opam  /home/user/.tmp-opam/lib/opam/
RUN    cd /home/user \
    && ./.tmp-opam/bin/k-configure-opam-dev

ADD --chown=user:user deps/wasm-semantics/deps/k/haskell-backend/src/main/native/haskell-backend/stack.yaml /home/user/.tmp-haskell/
ADD --chown=user:user deps/wasm-semantics/deps/k/haskell-backend/src/main/native/haskell-backend/kore/package.yaml /home/user/.tmp-haskell/kore/
RUN    cd /home/user/.tmp-haskell \
    && stack build --only-snapshot

ENV PATH=/home/user/.local/bin:/home/user/.cargo/bin:$PATH
