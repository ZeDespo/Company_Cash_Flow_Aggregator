pipeline {
    environment {
        registry = "adespotakis/capstone"
        registryCredential = 'dockerhub'
    }
    agent any
    stages {
        stage("Linting Django views") {
            steps {
                sh "pycodestyle cash_flow/cscf/views.py --max-line-length 140"
            }
        }
        stage("Building image") {
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
        stage("Deploy Django Application") {
            steps {
                sh "kubectl apply -f ./kubeconfigs/django-controller.json"
            }
        }
        stage("Deploy Load Balancer") {
            steps {
                sh "kubectl apply -f ./kubeconfigs/load-balancer-service.json"
            }
        }
    }
}