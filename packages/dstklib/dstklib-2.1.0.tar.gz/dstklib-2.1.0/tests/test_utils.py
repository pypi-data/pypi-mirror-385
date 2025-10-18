import pytest
from warnings import WarningMessage

from dstk.utils import *

def test_check_return_results(recwarn) -> None:

    with pytest.raises(ValueError, match="do not include the following"):
        check_return_results(return_list=['A', 'B', 'C'], callable_names=['B', 'C', 'D'], callable_type="workflow")

    check_return_results(return_list=['A', 'B', 'C'], callable_names=['B', 'C', 'A'], callable_type="workflow")

    returned_warning: WarningMessage = recwarn[0]
    warning_message: str = str(returned_warning.message)

    assert len(recwarn) == 1, "the lenght of recwarn must be exactly 1"
    assert warning_message == "The workflows will be returned in the execution order (['B', 'C', 'A']) not in the order you provided (['A', 'B', 'C']). Be careful when unpacking the results"