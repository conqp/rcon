pipeline {
  agent any
  stages {
    stage('Install build dependencies') {
      steps {
        sh 'pip install -U --upgrade pip pytest setuptools setuptools-git-version'
      }
    }

    stage('Install project') {
      steps {
        sh 'python3 setup.py install --user'
      }
    }

    stage('Run pytest') {
      steps {
        sh 'python3 -m pytest'
      }
    }

    stage('Prepare SonarQube') {
      steps {
        withSonarQubeEnv 'BF41A1F2-AXbeJg1gSMYOIOxzTbKL'
      }
    }

    stage('Wait for SonarQube analysis') {
      steps {
        waitForQualityGate()
      }
    }

  }
}