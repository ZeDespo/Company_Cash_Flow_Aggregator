pipeline {
    environment {
        registry = "adespotakis/capstone"
        registryCredential = 'dockerhub'
    }
    agent any
    stages {
        stage('Building image') {
            steps {
                script {
                    dockerImage = docker.build registry + ":$BUILD_NUMBER"
                }
            }
        }
        stage("Pushing image") {
            steps {
                script {
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                    }
                }
            }
        }
        stage("Remove local docker image") {
            steps {
                sh "docker rmi $registry:$BUILD_NUMBER"
            }
        }
    }
}