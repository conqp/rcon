pipeline {
  agent any
  stages {
    stage('pytest') {
      steps {
        sh '''mkdir -p /tmp/jenkins-venv
              python3 -m venv /tmp/jenkins-venv
              source /tmp/jenkins-venv/bin/activate
              pip install -U pytest setuptools setuptools-git-version
              ls -R
              python3 setup.py install
              pytest
'''
      }
    }

  }
}