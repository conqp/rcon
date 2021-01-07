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
        withSonarQubeEnv('SonarQube') {
          sh '/opt/sonar-scanner/bin/sonar-scanner'
        }

      }
    }

    stage('Wait for SonarQube analysis') {
      steps {
        waitForQualityGate()
      }
    }

  }
}