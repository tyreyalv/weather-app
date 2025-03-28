// Return Repository Name
String getRepoName() {
    return scm.getUserRemoteConfigs()[0].getUrl().tokenize('/')[3].split("\\.")[0]
}
pipeline {
    agent {
        kubernetes {
            defaultContainer 'kaniko'
            workspaceVolume genericEphemeralVolume(storageClassName: 'truenas-csi-rbd', requestsSize: '50Gi', accessModes: 'ReadWriteOnce')
            yaml """
kind: Pod
metadata:
  name: kaniko
spec:
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:debug
    imagePullPolicy: Always
    command:
    - /busybox/cat
    envFrom:
      - secretRef:
          name: registry-jenkins-url
    tty: true
    volumeMounts:
      - name: jenkins-docker-cfg
        mountPath: /kaniko/.docker
  volumes:
  - name: jenkins-docker-cfg
    projected:
      sources:
      - secret:
          name: jenkins-registry
          items:
            - key: .dockerconfigjson
              path: config.json
"""
        }
    }
    stages {
        stage('Checkout Repository') {
            steps {
                // Checkout Repository
                checkout scm
                // Get Repository Name
                script {
                    env.repoName = getRepoName()
                }
            }
        }
        //stage('Run Code Tests') {
        //}
        stage('Build with Kaniko and push to Harbor') {
            steps {
                container(name: 'kaniko', shell: '/busybox/sh') {
                    withEnv(['PATH+EXTRA=/busybox']) {
                        sh '''#!/busybox/sh
            /kaniko/executor -f /Dockerfile -c `pwd` --destination=$HARBOR/jenkins/$repoName:$GIT_BRANCH
            '''
                    }
                }
            }
        }
    }
}
