import pytest
from src.python_activator.api import read_root

def test_root():
	
	expected = {"Hello": "World"}

	# Act
	output = read_root()

	# Assert
	assert output == expected
	
def test_tootFail():
	
	expected = {"Hello": "Farid"}

	# Act
	output = read_root()

	# Assert
	assert output == expected
	
