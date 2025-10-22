
import pytest

from selenium_package.executors import RetryActionUntilNewFileHasBeenDetected

from selenium_package.utils.messages import *

from selenium_package.interfaces import BaseAction

from unittest.mock import MagicMock, patch

from pathlib import Path

@pytest.fixture
def empty_directory(tmp_path: Path) -> Path:
    return tmp_path

class TestRetryActionUntilNewFileHasBeenDetected:

    def test_if_raise_value_error_when_path_is_not_a_path_instance(self):
        with pytest.raises(ValueError) as e:
            RetryActionUntilNewFileHasBeenDetected(
                action=MagicMock(spec=BaseAction),
                path="not_a_path"
            )   

        assert str(e.value) == VARIABLE_MUST_BE_A_PATH_INSTANCE.format(variable_name="path")

    def test_if_old_files_count_is_correct(self, empty_directory: Path):
        
        assert isinstance(empty_directory, Path)
        
        executor_with_any_extension = RetryActionUntilNewFileHasBeenDetected(
            action=MagicMock(spec=BaseAction),
            path=empty_directory
        )

        executor_with_pdf_extension = RetryActionUntilNewFileHasBeenDetected(
            action=MagicMock(spec=BaseAction),
            path=empty_directory,
            file_extension='.pdf'
        )
        
        executor_with_xml_extension = RetryActionUntilNewFileHasBeenDetected(
            action=MagicMock(spec=BaseAction),
            path=empty_directory,
            file_extension='.xml'
        )

        executor_with_zip_extension = RetryActionUntilNewFileHasBeenDetected(
            action=MagicMock(spec=BaseAction),
            path=empty_directory,
            file_extension='.zip'
        )

        assert executor_with_any_extension.old_files_count == 0
        assert executor_with_pdf_extension.old_files_count == 0
        assert executor_with_xml_extension.old_files_count == 0
        assert executor_with_zip_extension.old_files_count == 0

    def test_if_condition_to_stop_is_not_met_when_no_new_file_is_detected(
        self, 
        empty_directory: Path, 
        ):
        executor = RetryActionUntilNewFileHasBeenDetected(
            action=MagicMock(spec=BaseAction),
            path=empty_directory
        )

        assert executor.is_condition_to_stop_met() == False
        
    def test_if_condition_to_stop_is_met_when_new_file_is_detected(
        self, 
        empty_directory: Path, 
        ):

        executor = RetryActionUntilNewFileHasBeenDetected(
            action=MagicMock(spec=BaseAction),
            path=empty_directory
        )

        with patch.object(executor, "_get_current_files_count", return_value=1):
            assert executor.is_condition_to_stop_met() == True
        

   