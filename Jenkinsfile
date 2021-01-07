pipeline {
  agent any
  stages {
    stage('pytest') {
      steps {
        sh '''mkdir -p /tmp/jenkins-venv
              python3 -m venv /tmp/jenkins-venv
              source /tmp/jenkins-venv/bin/activate
              pip install -U pytest
              pip install -r requirements.txt
              pytest
'''
      }
    }

  }
}
