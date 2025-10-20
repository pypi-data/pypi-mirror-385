import unittest

__all__ = ["test"]


def test() -> unittest.TextTestResult:
    loader: unittest.TestLoader = unittest.TestLoader()
    tests: unittest.TestSuite = loader.discover(start_dir="datarepr.tests")
    runner: unittest.TextTestRunner = unittest.TextTestRunner()
    result: unittest.TextTestResult = runner.run(tests)
    return result
