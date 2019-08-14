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
      steps {
        sh '''
          make deps -B
        '''
      }
    }
    stage('Build') {
      steps {
        sh '''
          make build -B -j4
        '''
      }
    }
    stage('Test') {
      parallel {
        stage('Exec OCaml') {
          steps {
            sh '''
              nprocs=$(nproc)
              [ "$nprocs" -gt '4' ] && nprocs=4
              make TEST_CONCRETE_BACKEND=ocaml test-execution -j"$nprocs"
            '''
          }
        }
        stage('Exec Java') {
          steps {
            sh '''
              nprocs=$(nproc)
              [ "$nprocs" -gt '4' ] && nprocs=4
              make TEST_CONCRETE_BACKEND=java test-execution -j"$nprocs"
            '''
          }
        }
        stage('Proofs Java') {
          steps {
            sh '''
              nprocs=$(nproc)
              [ "$nprocs" -gt '4' ] && nprocs=4
              make test-prove -j"$nprocs"
            '''
          }
        }
        stage('KLab Proofs Java') {
          steps {
            sh '''
              nprocs=$(nproc)
              [ "$nprocs" -gt '4' ] && nprocs=4
              make test-klab-prove -j"$nprocs"
            '''
          }
        }
      }
    }
  }
}
