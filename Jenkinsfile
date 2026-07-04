pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['qa', 'uat', 'prod'],
            description: 'Environment to run tests against'
        )

        choice(
            name: 'TEST_MARKER',
            choices: ['smoke', 'sanity', 'regression'],
            description: 'Pytest marker to execute'
        )

        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit'],
            description: 'Browser to run tests on'
        )

        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run browser in headless mode'
        )

        choice(
            name: 'VIDEO',
            choices: ['off', 'on', 'retain-on-failure'],
            description: 'Video recording option'
        )

        choice(
            name: 'TRACING',
            choices: ['off', 'on', 'retain-on-failure'],
            description: 'Playwright tracing option'
        )

        choice(
            name: 'SCREENSHOT',
            choices: ['off', 'on', 'only-on-failure'],
            description: 'Screenshot capture option'
        )
    }

    environment {
        PYTHON_VERSION = 'python3'
        PLAYWRIGHT_TIMEOUT = '30000'

        TEST_ENV = "${params.TEST_ENV}"
        BROWSER = "${params.BROWSER}"
        HEADLESS = "${params.HEADLESS}"
        VIDEO = "${params.VIDEO}"
        TRACING = "${params.TRACING}"
        SCREENSHOT = "${params.SCREENSHOT}"

        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh '''
                    rm -rf .venv
                    ${PYTHON_VERSION} -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Install Playwright Browsers') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m playwright install --with-deps ${BROWSER}
                '''
            }
        }

        stage('Prepare Reports Directory') {
            steps {
                sh '''
                    rm -rf reports
                    mkdir -p reports/allure-results
                    mkdir -p reports/junit
                    mkdir -p reports/screenshots
                    mkdir -p reports/traces
                    mkdir -p reports/videos
                    mkdir -p reports/logs
                '''
            }
        }

        stage('Run UI Tests') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'opencart-valid-login',
                        usernameVariable: 'VALID_EMAIL',
                        passwordVariable: 'VALID_PASSWORD'
                    )
                ]) {
                    sh '''
                        . .venv/bin/activate

                        pytest -m "${TEST_MARKER}" \
                            --env="${TEST_ENV}" \
                            --junitxml=reports/junit/results.xml
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Archiving test reports and artifacts...'

            junit allowEmptyResults: true, testResults: 'reports/junit/results.xml'

            archiveArtifacts(
                artifacts: 'reports/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }

        success {
            echo 'UI tests passed successfully.'
        }

        failure {
            echo 'UI tests failed. Check screenshots, traces, videos, logs, and Allure results.'
        }

        cleanup {
            sh '''
                rm -rf .venv
            '''
        }
    }
}