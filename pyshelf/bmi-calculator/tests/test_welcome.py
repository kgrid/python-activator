import re
import pytest
from bmi_calculator.bmi import calculate_bmi,get_bmi_category


def test_calculate_bmi_works():
    input= {
        "height":1.82,
        "weight":64,
        "unit_system":"metric"
    }
    test=calculate_bmi(input)
    assert test==19.32133800265668
    
    
    
    
def test_get_bmi_category_works():
    input= {
        "bmi":19.3
    }
    test=get_bmi_category(input)
    assert test=="Normal weight"    
    
def test_calculate_bmi_exception_missing_argument_name():
    input= {
        "weight":64,
        "unit_system":"metric"
    }
    with pytest.raises(KeyError, match="height"):
        calculate_bmi(input)
        
def test_calculate_bmi_exception_wrong_data_type():
    input= {
        "height":1.82,
        "weight":"64",
        "unit_system":"metric"
    }
    with pytest.raises(TypeError, match=re.escape("unsupported operand type(s) for /: 'str' and 'float'")):
        calculate_bmi(input) 
        
def test_get_bmi_category_exception_missing_argument_name():
    input= {
        "weight":19.3
    }
    with pytest.raises(KeyError, match="bmi"):
        get_bmi_category(input)
        
def test_get_bmi_category_exception_wrong_data_type():
    input= {
        "bmi":"19.3"
    }
    with pytest.raises(TypeError, match="'<' not supported between instances of 'str' and 'float'"):
        get_bmi_category(input)  
        
       
        
