pipeline {
  agent {
    dockerfile {
      reuseNode true
    }
  }
  options {
    ansiColor('xterm')
  }
  stages {
    stage('Init title') {
      when { changeRequest() }
      steps {
        script {
          currentBuild.displayName = "PR ${env.CHANGE_ID}: ${env.CHANGE_TITLE}"
        }
      }
    }
    stage('Dependencies') {
      parallel {
        stage('KWasm') {
          steps {
            sh '''
              make deps
            '''
          }
        }
        stage('Polkadot') {
          steps {
            sh '''
              make deps-polkadot
            '''
          }
        }
      }
    }
    stage('Build') {
      parallel {
        stage('KWasm (normal)') {
          steps {
            sh '''
              make build SUBDEFN=kwasm -j4
            '''
          }
        }
        stage('KWasm (coverage)') {
          steps {
            sh '''
              make build SUBDEFN=coverage -j4 KOMPILE_OPTIONS='--coverage'
            '''
          }
        }
        stage('Polkadot') {
          steps {
            sh '''
              make polkadot-runtime-source
            '''
          }
        }
      }
    }
    stage('Test') {
      parallel {
        stage('Can Build Specs') {
          options { timeout(time: 1, unit: 'MINUTES') }
          steps {
            sh '''
              make test-can-build-specs -j6
            '''
          }
        }
        stage('Python Config') {
          options { timeout(time: 1, unit: 'MINUTES') }
          steps {
            sh '''
              make test-python-config
            '''
          }
        }
        stage('Fuse Rules Simple') {
          options { timeout(time: 20, unit: 'MINUTES') }
          steps {
            sh '''
              make test-fuse-rules
            '''
          }
        }
      }
    }
  }
}
