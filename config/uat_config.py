UAT_CONFIG = {
    "env": "uat",

    "base_url": "https://tutorialsninja.com/demo/index.php?route=common/home",

    "browser": "chromium",
    "headed": False,
    "slow_mo": 0,

    "timeout": 30000,

    "viewport": {
        "width": 1366,
        "height": 768
    },

    "locale": "en-AU",
    "timezone_id": "Australia/Melbourne",

    "video": "retain-on-failure",
    "tracing": "retain-on-failure",
    "screenshot": "only-on-failure",

    "ignore_https_errors": True,
    "accept_downloads": True,

    "credentials": {
        "valid_email": "uat_user@test.com",
        "valid_password": "uat_password"
    }
}