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

        booleanParam(
            name: 'TESTRAIL_ENABLED',
            defaultValue: true,
            description: 'Publish linked automation results to TestRail'
        )

        booleanParam(
            name: 'TESTRAIL_CLOSE_RUN',
            defaultValue: false,
            description: 'Close the TestRail run after publishing results'
        )

        booleanParam(
            name: 'TESTRAIL_FAIL_ON_ERROR',
            defaultValue: false,
            description: 'Fail the Jenkins build when TestRail publishing fails'
        )
    }

    environment {
        // ===================================================================
        // PYTHON AND PLAYWRIGHT
        // ===================================================================

        PYTHON_EXE = 'python'
        PLAYWRIGHT_TIMEOUT = '30000'

        TEST_ENV = "${params.TEST_ENV}"
        TEST_MARKER = "${params.TEST_MARKER}"
        BROWSER = "${params.BROWSER}"
        HEADLESS = "${params.HEADLESS}"
        VIDEO = "${params.VIDEO}"
        TRACING = "${params.TRACING}"
        SCREENSHOT = "${params.SCREENSHOT}"

        // ===================================================================
        // TESTRAIL - NON-SECRET CONFIGURATION
        // ===================================================================

        TESTRAIL_ENABLED = "${params.TESTRAIL_ENABLED}"
        TESTRAIL_URL = 'https://opencart.testrail.io'
        TESTRAIL_PROJECT_ID = '2'

        TESTRAIL_CLOSE_RUN = "${params.TESTRAIL_CLOSE_RUN}"
        TESTRAIL_FAIL_ON_ERROR = "${params.TESTRAIL_FAIL_ON_ERROR}"

        // The framework automatically uses BUILD_NUMBER as the version.
        TESTRAIL_VERSION = "${env.BUILD_NUMBER}"

        // No suite ID is required for the current single-repository project.
        // Do not configure TESTRAIL_RUN_ID when a new run should be created.

        // ===================================================================
        // GENERAL CI SETTINGS
        // ===================================================================

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
                    @echo off

                    echo Current workspace:
                    cd

                    echo.
                    echo Project files:
                    dir
                '''
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat '''
                    @echo off

                    if exist .venv (
                        echo Removing existing virtual environment...
                        rmdir /s /q .venv
                    )

                    echo Creating virtual environment...
                    %PYTHON_EXE% -m venv .venv

                    echo Upgrading pip...
                    .venv\\Scripts\\python.exe -m pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    @echo off

                    echo Installing Python dependencies...
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                '''
            }
        }

        stage('Install Playwright Browser') {
            steps {
                bat '''
                    @echo off

                    echo Installing Playwright browser: %BROWSER%
                    .venv\\Scripts\\python.exe -m playwright install %BROWSER%
                '''
            }
        }

        stage('Prepare Reports Directory') {
            steps {
                bat '''
                    @echo off

                    echo Cleaning previous reports...

                    if exist reports (
                        rmdir /s /q reports
                    )

                    mkdir reports
                    mkdir reports\\allure-results
                    mkdir reports\\junit
                    mkdir reports\\screenshots
                    mkdir reports\\traces
                    mkdir reports\\videos
                    mkdir reports\\logs

                    echo Report directories created successfully.
                '''
            }
        }

        stage('Run UI Tests') {
            steps {
                /*
                 * Jenkins credential:
                 *
                 * Kind     : Username with password
                 * ID       : testrail-api
                 * Username : TestRail login email
                 * Password : TestRail API key
                 *
                 * The framework reads these as environment variables:
                 * TESTRAIL_USER
                 * TESTRAIL_API_KEY
                 */
                withCredentials([
                    usernamePassword(
                        credentialsId: 'testrail-api',
                        usernameVariable: 'TESTRAIL_USER',
                        passwordVariable: 'TESTRAIL_API_KEY'
                    )
                ]) {
                    bat '''
                        @echo off

                        echo ==================================================
                        echo Test Execution Configuration
                        echo ==================================================
                        echo Environment       : %TEST_ENV%
                        echo Marker            : %TEST_MARKER%
                        echo Browser           : %BROWSER%
                        echo Headless          : %HEADLESS%
                        echo Video             : %VIDEO%
                        echo Tracing           : %TRACING%
                        echo Screenshot        : %SCREENSHOT%
                        echo TestRail Enabled  : %TESTRAIL_ENABLED%
                        echo TestRail Project  : %TESTRAIL_PROJECT_ID%
                        echo Build Number      : %BUILD_NUMBER%
                        echo ==================================================

                        if "%TEST_MARKER%"=="all" (
                            echo Running all tests...

                            .venv\\Scripts\\python.exe -m pytest ^
                                --env="%TEST_ENV%" ^
                                --alluredir="%WORKSPACE%\\reports\\allure-results" ^
                                --junitxml="%WORKSPACE%\\reports\\junit\\results.xml"
                        ) else (
                            echo Running tests with marker: %TEST_MARKER%

                            .venv\\Scripts\\python.exe -m pytest ^
                                -m "%TEST_MARKER%" ^
                                --env="%TEST_ENV%" ^
                                --alluredir="%WORKSPACE%\\reports\\allure-results" ^
                                --junitxml="%WORKSPACE%\\reports\\junit\\results.xml"
                        )
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Publishing JUnit and Allure reports...'

            junit(
                allowEmptyResults: true,
                testResults: 'reports/junit/results.xml'
            )

            allure([
                includeProperties: false,
                jdk: '',
                properties: [],
                reportBuildPolicy: 'ALWAYS',
                results: [
                    [path: 'reports/allure-results']
                ]
            ])

            archiveArtifacts(
                artifacts: 'reports/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }

        success {
            echo 'UI tests completed successfully.'
            echo 'Results were published to Allure and TestRail.'
        }

        unstable {
            echo 'The build is unstable. Review the JUnit and Allure reports.'
        }

        failure {
            echo 'UI tests failed.'
            echo 'Check Allure, TestRail, screenshots, traces, videos, and logs.'
        }

        cleanup {
            bat '''
                @echo off

                if exist .venv (
                    echo Removing virtual environment...
                    rmdir /s /q .venv
                )
            '''
        }
    }
}