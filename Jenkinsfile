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
        withSonarQubeEnv(installationName: 'SonarQube', credentialsId: '4cdfb484-a052-41be-8739-3e1c232b5f38') {
          sh '/opt/sonar-scanner/bin/sonar-scanner -Dsonar.projectKey=rcon'
          waitForQualityGate(credentialsId: '4cdfb484-a052-41be-8739-3e1c232b5f38')
        }

      }
    }

  }
}