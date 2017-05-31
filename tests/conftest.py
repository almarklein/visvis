import os
import sys
import pytest

@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    if os.getenv('TEST_INSTALL') not in ('1', 'true'):
        sys.path.insert(0, '..')
