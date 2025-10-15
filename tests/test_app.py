import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root path redirects to index.html"""
    response = client.get("/")
    assert response.status_code in [200, 307]  # Aceptar tanto redirección como respuesta directa
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_success():
    """Test successful activity signup"""
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up test@mergington.edu for Chess Club"

    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test signing up an already registered participant"""
    # First signup
    client.post("/activities/Programming Class/signup?email=test2@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Programming Class/signup?email=test2@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_success():
    """Test successful unregistration from activity"""
    # First signup
    email = "testunregister@mergington.edu"
    activity = "Math Olympiad"
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Then unregister
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity}"

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """Test unregistering a participant that is not registered"""
    response = client.delete("/activities/Debate Team/signup?email=notregistered@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in activity"

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"