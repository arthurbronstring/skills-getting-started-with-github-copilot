# Test Commands

## Run all tests
```bash
python -m pytest tests/ -v
```

## Run tests with coverage
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

## Run tests for specific functionality
```bash
# Test only signup functionality
python -m pytest tests/test_app.py::TestSignupForActivity -v

# Test only unregister functionality  
python -m pytest tests/test_app.py::TestUnregisterFromActivity -v

# Test integration scenarios
python -m pytest tests/test_app.py::TestIntegrationScenarios -v
```

## Install test dependencies
```bash
pip install -r requirements.txt
```