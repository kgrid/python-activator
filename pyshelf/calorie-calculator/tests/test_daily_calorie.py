import pytest
from calorie_calculator.daily_calorie import calculate_daily_calorie_needs


def test_calculate_daily_calorie_needs_works():
    input= {
        "gender": "male",
        "weight": 70,
        "height": 175,
        "age": 30,
        "activity_level": "moderately active",
        "unit_system": "metric"
    }
    test=calculate_daily_calorie_needs(input)
    assert test==2628.2838500000003
    
def test_calculate_daily_calorie_needs_exception_missing_argument_gender():
    input= {
        "weight": 70,
        "height": 175,
        "age": 30,
        "activity_level": "moderately active",
        "unit_system": "metric"
    }
    with pytest.raises(KeyError, match="gender"):
        calculate_daily_calorie_needs(input)
        
def test_calculate_daily_calorie_needs_exception_wrong_data_type():
    input= {
        "gender": "male",
        "weight": "70",
        "height": 175,
        "age": 30,
        "activity_level": "moderately active",
        "unit_system": "metric"
    }
    with pytest.raises(TypeError, match="can't multiply sequence by non-int of type 'float'"):
        calculate_daily_calorie_needs(input) 
        
