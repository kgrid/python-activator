import pytest
from python_multiartifact_v1_0.main import generate_page


def test_welcome_works():
    input= {
        "name":"John Doe",
        "spaces":10,
        "size":20
    }
    test=generate_page(input)
    assert test=="<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\"><style>p{font-size:20}</style></head><body><p>Welcome to Knowledge Grid,   John Doe</p></body></html>"
    
def test_welcome_exception_missing_argument_name():
    input= {
        "username":"John Doe",
        "spaces":10,
        "size":20
    }
    with pytest.raises(KeyError, match="name"):
        generate_page(input)
        
def test_welcome_exception_wrong_data_type():
    input= {
        "name":"John Doe",
        "spaces":"10",
        "size":20
    }
    with pytest.raises(TypeError, match="'str' object cannot be interpreted as an integer"):
        generate_page(input) 
