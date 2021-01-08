pipeline {
  agent any
  stages {
    stage('Install build dependencies') {
      steps {
        sh 'pip install -U --upgrade pytest'
      }
    }

    stage('Run pytest') {
      steps {
        sh 'python3 -m pytest'
      }
    }

    stage('Run SonarQube') {
      steps {
        withSonarQubeEnv(installationName: 'rcon', credentialsId: '4cdfb484-a052-41be-8739-3e1c232b5f38') {
          sh '/opt/sonar-scanner/bin/sonar-scanner'
        }

      }
    }

    stage('Send Email') {
      steps {
        mail(subject: '[rcon] build successful', body: 'https://jenkins.richard-neumann.de/blue/organizations/jenkins/rcon/activity', from: 'jenkins@richard-neumann.de', to: 'mail@richard-neumann.de')
      }
    }

  }
}