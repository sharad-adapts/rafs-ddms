# How to run integration test

## Local running
1. Install `requirements.txt` and `requirements-tests.in`
2. Run:
    ```
    pytest -n auto --dist loadscope tests/integration/tests/{test_file} --ddms-base-url {DDMS_BASE_URL}
    ```

##  Run in integration test as standalone
1. Install requests
    ```
    python -m venv integration_env
    source integration_env/bin/activate
    pip install requests
    ````
2. Run:
    ```
    pytest -n auto --dist loadscope tests/integration/tests/{test_file} --ddms-base-url {DDMS_BASE_URL} --bearer-token {TOKEN}
    ```
