pipeline {
  agent {
    dockerfile {
      label 'docker'
      additionalBuildArgs '--build-arg K_COMMIT=$(cd deps/wasm-semantics/deps/k && git rev-parse --short=7 HEAD) --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g)'
    }
  }
  options { ansiColor('xterm') }
  stages {
    stage('Init title') {
      when { changeRequest() }
      steps { script { currentBuild.displayName = "PR ${env.CHANGE_ID}: ${env.CHANGE_TITLE}" } }
    }
    stage('Build') {
      parallel {
        stage('KWasm (normal)')   { steps { sh 'make build -j4'                } }
        stage('KWasm (coverage)') { steps { sh 'make build -j4 BUILD=coverage' } }
        stage('Polkadot')         { steps { sh 'make polkadot-runtime-source ; git checkout src/ ;' } }
      }
    }
    stage('Test') {
      options { timeout(time: 20, unit: 'MINUTES') }
      parallel {
        stage('Prove High Level Specs') { steps { sh 'make prove-specs -j6'      } }
        stage('Python Config')          { steps { sh 'make test-python-config'   } }
        stage('Run Search')             { steps { sh 'make test-search'          } }
      }
    }
  }
}
