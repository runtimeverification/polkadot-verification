ARG K_COMMIT
FROM runtimeverificationinc/kframework-k:ubuntu-bionic-${K_COMMIT}

RUN    apt-get update           \
    && apt-get upgrade --yes    \
    && apt-get install --yes    \
                        cmake   \
                        curl    \
                        pandoc

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID user && useradd -m -u $USER_ID -s /bin/sh -g user user

USER user:user
WORKDIR /home/user

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain nightly-2020-04-21 --target wasm32-unknown-unknown
RUN cargo install --git https://github.com/alexcrichton/wasm-gc --branch wasm-gc-api-0.1.11

RUN    git clone 'https://github.com/WebAssembly/wabt' --branch 1.0.13 wabt \
    && cd wabt                                                              \
    && mkdir build                                                          \
    && cd build                                                             \
    && cmake ..                                                             \
    && cmake --build .

ENV LD_LIBRARY_PATH=/usr/local/lib
ENV PATH=/home/user/wabt/build:/home/user/.local/bin:/home/user/.cargo/bin:$PATH
