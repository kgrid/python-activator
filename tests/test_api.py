import pytest
from src.python_activator.api import hello,execute_endpoint

def test_root():
	
	expected = {"Hello": "World"}

	# Act
	output = hello()

	# Assert
	assert output == expected
	
def test_hard_coded_root_nessage_doesnt_know_Farid():
	
	expected = {"Hello": "Farid"}

	# Act
	output = hello()

	# Assert
	assert output != expected
 
 

 
