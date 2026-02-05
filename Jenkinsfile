pipeline {
    agent any

    environment {
        IMAGE_NAME = "fekry34455/backend-reddit"
        IMAGE_TAG  = "latest"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

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
        // Create .env File
        // ============================
      stage('Create Env File') {
    steps {
        withCredentials([
            string(credentialsId: 'DJANGO_SECRET_KEY', variable: 'DJANGO_SECRET_KEY')
        ]) {
            sh '''
cat > .env <<EOF
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=True

DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*

DATABASE_URL=sqlite:///db.sqlite3

DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

USE_S3=False
AWS_REGION=us-east-1

EOF
'''
        }
    }
}



        stage('Migrate Database') {
            steps {
                sh '''
                  . .venv/bin/activate
                  python manage.py migrate
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                  . .venv/bin/activate
                  pytest || true
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                  docker build -t backend .
                  docker tag backend ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                  trivy image ${IMAGE_NAME}:${IMAGE_TAG} || true
                '''
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'docker-hub-credentials',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
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
