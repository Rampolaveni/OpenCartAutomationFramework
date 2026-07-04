pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['qa', 'uat', 'prod'],
            description: 'Environment to run tests against'
        )

        choice(
            name: 'TEST_MARKER',
            choices: ['all', 'smoke', 'sanity', 'regression'],
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
        PYTHON_EXE = 'python'
        PLAYWRIGHT_TIMEOUT = '30000'

        TEST_ENV = "${params.TEST_ENV}"
        TEST_MARKER = "${params.TEST_MARKER}"
        BROWSER = "${params.BROWSER}"
        HEADLESS = "${params.HEADLESS}"
        VIDEO = "${params.VIDEO}"
        TRACING = "${params.TRACING}"
        SCREENSHOT = "${params.SCREENSHOT}"

        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONUNBUFFERED = '1'
        CI = 'true'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Verify Workspace') {
            steps {
                bat '''
                    echo Current workspace:
                    cd

                    echo Project files:
                    dir
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                    if exist .venv rmdir /s /q .venv

                    %PYTHON_EXE% -m venv .venv

                    .venv\\Scripts\\python.exe -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Install Playwright Browsers') {
            steps {
                bat '''
                    .venv\\Scripts\\python.exe -m playwright install %BROWSER%
                '''
            }
        }

        stage('Prepare Reports Directory') {
            steps {
                bat '''
                    if exist reports rmdir /s /q reports

                    mkdir reports
                    mkdir reports\\allure-results
                    mkdir reports\\junit
                    mkdir reports\\screenshots
                    mkdir reports\\traces
                    mkdir reports\\videos
                    mkdir reports\\logs
                '''
            }
        }

        stage('Run UI Tests') {
            steps {
                bat '''
                    if "%TEST_MARKER%"=="all" (
                        .venv\\Scripts\\python.exe -m pytest --env="%TEST_ENV%" --junitxml=reports\\junit\\results.xml
                    ) else (
                        .venv\\Scripts\\python.exe -m pytest -m "%TEST_MARKER%" --env="%TEST_ENV%" --junitxml=reports\\junit\\results.xml
                    )
                '''
            }
        }
    }

    post {
        always {
            echo 'Publishing JUnit and Allure reports...'

            junit allowEmptyResults: true, testResults: 'reports/junit/results.xml'

            allure([
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [[path: 'reports/allure-results']]
            ])

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
            echo 'UI tests failed. Check Allure report, screenshots, traces, videos, and logs.'
        }

        cleanup {
            bat '''
                if exist .venv rmdir /s /q .venv
            '''
        }
    }
}