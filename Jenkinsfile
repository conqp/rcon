pipeline {
  agent none
  stages {
    stage('pytest') {
      steps {
        sh '''python3 -m venv /var/build/jenkins
              source /var/build/jenkins/bin/activate
              pip install -U pytest
              pip install -r requirements.txt
              pytest
'''
      }
    }

  }
}
