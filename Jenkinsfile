pipeline {
    environment {
        registryBlue = "adespotakis/capstone"
        registryGreen = "adespotakis/capstone-backup"
        registryCredential = 'dockerhub'
    }
    agent any
    stages {
        stage("Linting Django views") {
            steps {
                sh "pycodestyle cash_flow/cscf/views.py --max-line-length 140"
            }
        }
        stage("Building blue and green images") {
            steps {
                script {
                    dockerImageBlue = docker.build registryBlue + ":$BUILD_NUMBER"
                    dockerImageGreen = docker.build registryGreen + ":$BUILD_NUMBER"
                }
            }
        }
        stage("Pushing images") {
            steps {
                script {
                    docker.withRegistry( '', registryCredential ) {
                        dockerImageBlue.push()
                        dockerImageGreen.push()
                    }
                }
            }
        }
        stage("Remove local docker images") {
            steps {
                sh "docker rmi $registryBlue:$BUILD_NUMBER"
                sh "docker rmi $registryGreen:$BUILD_NUMBER"
            }
        }
    }
}