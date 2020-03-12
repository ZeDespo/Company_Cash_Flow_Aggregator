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
                sh "pycodestyle blue/cash_flow/cscf/views.py --max-line-length 140"
                sh "pycodestyle green/cash_flow/cscf/views.py --max-line-length 140"
            }
        }
        stage("Building blue and green images") {
            steps {
                script {
                    dockerImageBlue = docker.build(registryBlue + ":$BUILD_NUMBER", "blue/")
                    dockerImageGreen = docker.build(registryGreen + ":$BUILD_NUMBER", "green/")
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
        stage("Switch context") {
            steps {
                sh "kubectl config use-context arn:aws:eks:us-west-2:929484179881:cluster/capstone-web-app"
            }
        }
    }
}