pipeline {
  agent any

  environment {
    IMAGE_NAME = 'fraud-detection-api'
    IMAGE_TAG = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Lint') {
      steps {
        sh 'python -m pip install -r requirements.txt'
        sh 'python -m ruff check src tests'
      }
    }
    stage('Test') {
      steps {
        sh 'python -m pytest'
      }
    }
    stage('Build') {
      steps {
        sh 'python -m fraud_detection.models.train --no-tune'
      }
    }
    stage('Docker Build') {
      steps {
        sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .'
      }
    }
    stage('Docker Push') {
      when { expression { return env.DOCKER_REGISTRY != null && env.DOCKER_REGISTRY != '' } }
      steps {
        sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
        sh 'docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}'
      }
    }
    stage('Deploy') {
      steps {
        sh 'kubectl apply -f infra/kubernetes/'
      }
    }
    stage('Verification') {
      steps {
        sh 'kubectl rollout status deployment/fraud-detection-api -n fraud-detection --timeout=120s'
      }
    }
  }
}
