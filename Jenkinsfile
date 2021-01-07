pipeline {
  agent any
  stages {
    stage('Install build dependencies') {
      steps {
        sh '''
              pip install -U --update pip pytest setuptools setuptools-git-version'''
      }
    }

    stage('Install pytest') {
      steps {
        sh 'python3 setup.py install --user'
      }
    }

    stage('Run pytest') {
      steps {
        sh 'python3 -m pytest'
      }
    }

  }
}