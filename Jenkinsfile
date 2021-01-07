pipeline {
  agent any
  stages {
    stage('Create temporary directory') {
      steps {
        sh 'mkdir -p /tmp/jenkins-venv'
      }
    }

    stage('Create virtual env') {
      steps {
        sh '''
              python3 -m venv /tmp/jenkins-venv'''
      }
    }

    stage('Start virtual env') {
      steps {
        sh '              source /tmp/jenkins-venv/bin/activate'
      }
    }

    stage('Install build dependencies') {
      steps {
        sh '''
              pip install -U pytest setuptools setuptools-git-version'''
      }
    }

    stage('Install pytest') {
      steps {
        sh 'python3 setup.py install --user'
      }
    }

    stage('Run pytest') {
      steps {
        sh 'pytest'
      }
    }

  }
}