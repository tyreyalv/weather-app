// Return Repository Name
String getRepoName() {
    return scm.getUserRemoteConfigs()[0].getUrl().tokenize('/')[3].split("\\.")[0]
}
pipeline {
    agent {
        kubernetes {
            defaultContainer 'kaniko'
            workspaceVolume genericPVC(accessModes: 'ReadWriteOnce', requestsSize: "50Gi")
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
    
    environment {
        DISCORD_WEBHOOK = credentials('discord-webhook-url')
    }
    
    stages {
        stage('Notify Build Started') {
            steps {
                script {
                    discordSend description: "🔄 **Building Docker image**\nBranch: ${env.GIT_BRANCH}\nBuild: #${env.BUILD_NUMBER}", 
                              footer: "Started at ${new Date().format('yyyy-MM-dd HH:mm:ss')}", 
                              link: env.BUILD_URL, 
                              result: "UNSTABLE", // Yellow color for "in progress"
                              title: "🚀 Build Started: ${env.JOB_NAME}", 
                              webhookURL: DISCORD_WEBHOOK
                }
            }
        }
        
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
    
    post {
        success {
            script {
                discordSend description: "✅ **Successfully built and pushed image**\nRepository: ${env.repoName}\nBranch: ${env.GIT_BRANCH}\nTag: ${env.GIT_BRANCH}\nDestination: https://registry.tyreyalv.com/jenkins/${env.repoName}:${env.GIT_BRANCH}", 
                          footer: "Build #${env.BUILD_NUMBER} • Completed in ${currentBuild.durationString.replace(' and counting', '')}", 
                          link: env.BUILD_URL, 
                          result: "SUCCESS", // Green color
                          title: "✅ Build Successful", 
                          webhookURL: DISCORD_WEBHOOK
            }
        }
        
        failure {
            script {
                discordSend description: "❌ **Build failed**\nRepository: ${env.repoName}\nBranch: ${env.GIT_BRANCH}\n\nCheck the logs for details.", 
                          footer: "Build #${env.BUILD_NUMBER} • Failed after ${currentBuild.durationString.replace(' and counting', '')}", 
                          link: env.BUILD_URL, 
                          result: "FAILURE", // Red color
                          title: "❌ Build Failed", 
                          webhookURL: DISCORD_WEBHOOK
            }
        }
        
        aborted {
            script {
                discordSend description: "⚠️ **Build aborted**\nRepository: ${env.repoName}\nBranch: ${env.GIT_BRANCH}", 
                          footer: "Build #${env.BUILD_NUMBER}", 
                          link: env.BUILD_URL, 
                          result: "ABORTED", // Grey color
                          title: "⚠️ Build Aborted", 
                          webhookURL: DISCORD_WEBHOOK
            }
        }
    }
}
