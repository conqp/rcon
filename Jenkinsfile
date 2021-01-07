pipeline {
  agent none
  stages {
    stage('pytest') {
      steps {
        sh '''python3 -m venv /var/build/jenkins
source env/bin/activate
'''
      }
    }

  }
}