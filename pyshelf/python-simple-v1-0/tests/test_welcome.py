import pytest
from python_simple_v1_0.welcome import welcome


def test_welcome_works():
    input= {
        "name":"John Doe",
        "spaces":0
    }
    test=welcome(input)
    assert test=="Welcome to Knowledge Grid,John Doe"
    
def test_welcome_exception_missing_argument_name():
    input= {
        "username":"John Doe",
        "spaces":0
    }
    with pytest.raises(KeyError, match="name"):
        welcome(input)
        
def test_welcome_exception_wrong_data_type():
    input= {
        "name":"John Doe",
        "spaces":"5"
    }
    with pytest.raises(TypeError, match="'str' object cannot be interpreted as an integer"):
        welcome(input) 
