import pytest
from src.python_activator.api import hello,execute_endpoint
#from fastapi.testclient import TestClient
from src.test.test_fastapi_exceptions import app  # Assuming your FastAPI app instance is named `app`
def test_root():
	
	expected = {"Hello": "World9"}

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
 
def test_how_exceptions_are_handled_in_apis():
    #client = TestClient(app)
    #response = client.get("/item/foo")
    #assert response.status_code == 200
    #assert response.json() == {"item": "The Foo Wrestlers"}
    assert 1!=1

 
