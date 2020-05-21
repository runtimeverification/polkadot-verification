pipeline {
  agent { dockerfile { } }
  options { ansiColor('xterm') }
  stages {
    stage('Init title') {
      when { changeRequest() }
      steps { script { currentBuild.displayName = "PR ${env.CHANGE_ID}: ${env.CHANGE_TITLE}" } }
    }
    stage('KWasm Dependencies') { steps { sh 'make deps' } }
    stage('Build') {
      parallel {
        stage('KWasm (normal)')   { steps { sh 'make build SUBDEFN=kwasm -j4'                               } }
        stage('KWasm (coverage)') { steps { sh 'make build SUBDEFN=coverage -j4 KOMPILE_OPTIONS=--coverage' } }
        // stage('Polkadot')         { steps { sh 'make polkadot-runtime-source'                               } }
      }
    }
    stage('Test') {
      options { timeout(time: 20, unit: 'MINUTES') }
      parallel {
        stage('Prove High Level Specs') { steps { sh 'make prove-specs -j6'      } }
        stage('Python Config')          { steps { sh 'make test-python-config'   } }
        stage('Merge Rules')            { steps { sh 'make test-merge-rules -j8' } }
        stage('Run Search')             { steps { sh 'make test-search'          } }
      }
    }
  }
}
