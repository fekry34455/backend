pipeline {
    agent any

    environment {
        IMAGE_NAME = "fekry34455/backend-reddit"
        IMAGE_TAG  = "latest"
    }

    stages {

        // ============================
        // Checkout Source Code
        // ============================
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ============================
        // Setup Python & Install Deps
        // ============================
        stage('Install Dependencies') {
            steps {
                sh '''
                  python3 -m venv .venv
                  . .venv/bin/activate
                  pip install --upgrade pip
                  pip install -r requirements.txt
                '''
            }
        }

        // ============================
        // Run Django Migrations
        // ============================
        stage('Migrate Database') {
            steps {
                sh '''
                  . .venv/bin/activate
                  python manage.py migrate
                '''
            }
        }

        // ============================
        // Run Tests (Optional)
        // ============================
        stage('Run Tests') {
            steps {
                sh '''
                  . .venv/bin/activate
                  pytest || true
                '''
            }
        }

        // ============================
        // Build Docker Image
        // ============================
        stage('Docker Build') {
            steps {
                sh '''
                  docker build -t backend .
                  docker tag backend ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        // ============================
        // Trivy Scan
        // ============================
        stage('Trivy Scan') {
            steps {
                sh '''
                  trivy image ${IMAGE_NAME}:${IMAGE_TAG} || true
                '''
            }
        }

        // ============================
        // Push To DockerHub
        // ============================
        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                      docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Backend Pipeline Success"
        }
        failure {
            echo "❌ Backend Pipeline Failed"
        }
        always {
            sh 'docker logout || true'
        }
    }
}
