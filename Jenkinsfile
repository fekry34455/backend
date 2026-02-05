pipeline {
    agent any

    parameters {
        choice(
            name: 'BUILD_BACKEND',
            choices: ['True', 'False'],
            description: 'Force backend build even if no changes detected'
        )
    }

    environment {
        USE_S3      = 'False'
        AWS_REGION = 'us-east-1'
        BACKEND_IMAGE = 'backend-app'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        /* ============================
           Checkout
        ============================ */
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /* ============================
           Detect Backend Changes
        ============================ */
   stage('Detect Backend Changes') {
  steps {
    script {
      def baseRef = env.GIT_PREVIOUS_SUCCESSFUL_COMMIT ?: 'HEAD~1'

      def changes = sh(
        script: "git diff --name-only ${baseRef}...HEAD -- src/backend/",
        returnStdout: true
      ).trim()

      env.BACKEND_CHANGED = changes ? 'true' : 'false'
      echo "Backend changed: ${env.BACKEND_CHANGED}"
    }
  }
}


        /* ============================
           Build & Test Backend
        ============================ */
        stage('Build & Test Backend') {
            when {
                expression {
                    env.BACKEND_CHANGED == "true" || params.BUILD_BACKEND == "True"
                }
            }

            steps {

                /* Python Environment */
                sh '''
                  python3 -m venv .venv
                  . .venv/bin/activate
                  pip install --upgrade pip
                  pip install -r src/backend/requirements.txt
                '''

                /* OWASP Dependency Check */
                sh '''
                  dependency-check.sh \
                  --project "backend-app" \
                  --scan src/backend/requirements.txt \
                  --format HTML \
                  --failOnCVSS 7 || true
                '''

                /* Create .env */
                withCredentials([
                  string(credentialsId: 'DJANGO_SECRET_KEY', variable: 'DJANGO_SECRET_KEY')
                ]) {
                    sh '''
                      cat > src/backend/.env <<EOF
USE_S3=False
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///./db.sqlite3
DJANGO_ALLOWED_HOSTS=*
EOF
                    '''
                }

                /* Migrate */
                sh '''
                  . .venv/bin/activate
                  cd src/backend
                  python manage.py migrate
                '''

                /* Tests */
                sh '''
                  . .venv/bin/activate
                  cd src/backend
                  pytest --cov --cov-report=xml
                '''

                /* SonarQube */
                withSonarQubeEnv('sonarqube') {
                    sh '''
                      cd src/backend
                      sonar-scanner \
                      -Dsonar.projectKey=backend-app \
                      -Dsonar.projectName=Backend-App \
                      -Dsonar.sources=. \
                      -Dsonar.python.coverage.reportPaths=coverage.xml \
                      -Dsonar.python.version=3.12
                    '''
                }

                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }

                /* Build Docker Image */
                script {
                    env.COMMIT_SHA = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()
                }

                sh '''
                  cd src/backend
                  docker build -t backend-app:${COMMIT_SHA} .
                '''

                /* Trivy Scan */
                sh '''
                  trivy image backend-app:${COMMIT_SHA} \
                  --severity HIGH,CRITICAL \
                  --exit-code 1 || true
                '''

                /* Push To ECR */
                withCredentials([
                  [$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'AWS_ECR_CREDS'],
                  string(credentialsId: 'AWS_ECR_ACCOUNT_URL', variable: 'AWS_ECR_ACCOUNT_URL')
                ]) {
                    sh '''
                      aws ecr get-login-password --region ${AWS_REGION} \
                      | docker login --username AWS --password-stdin ${AWS_ECR_ACCOUNT_URL}

                      docker tag backend-app:${COMMIT_SHA} \
                      ${AWS_ECR_ACCOUNT_URL}/backend-app:${COMMIT_SHA}

                      docker push ${AWS_ECR_ACCOUNT_URL}/backend-app:${COMMIT_SHA}
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
    }
}
