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
          make deps deps-polkadot -j2
        '''
      }
    }
    stage('Build') {
      steps {
        sh '''
          make build -j4
        '''
      }
    }
    stage('Polkadot Runtime') {
      steps {
        sh '''
          make polkadot-runtime
        '''
      }
    }
  }
}
