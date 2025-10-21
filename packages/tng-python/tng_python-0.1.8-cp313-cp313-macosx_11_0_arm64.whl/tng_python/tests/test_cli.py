import unittest
from unittest import mock

from tng_python.cli import detect_mock_library


class TestCliDetectMockLibrary(unittest.TestCase):
    def test_detect_mock_library(self) -> None:
        tested_libraries = [
            ("pytest-mock", "pytest-mock"),
            ("doublex", "doublex"),
            ("flexmock", "flexmock"),
            ("sure", "sure"),
            ("mock", "mock"),
            ("", "unittest.mock"),  # Simulating no mock library specified
        ]
        for library, expected in tested_libraries:
            with self.subTest(mock_library=library, expected=expected):
                with mock.patch("tng_python.cli.get_dependency_content", return_value=f"{library}\n"):
                    with mock.patch("tng_python.cli.importlib.import_module"):
                        detected_library = detect_mock_library()
                        assert detected_library == expected
