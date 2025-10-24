"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in school plays and learn acting techniques",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        }
    })


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_success(self):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Drama Club" in data
        
        # Verify structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Drama Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Drama Club"
        
        # Verify the student was added to the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Drama Club"]["participants"]
    
    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_with_special_characters_in_name(self):
        """Test signup with URL encoding for activity names with special characters"""
        # Add an activity with special characters for testing
        activities["Art & Craft"] = {
            "description": "Creative arts and crafts",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 15,
            "participants": []
        }
        
        response = client.post(
            "/activities/Art & Craft/signup?email=artist@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up artist@mergington.edu for Art & Craft"


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify the student was removed from the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        # Verify other participant is still there
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self):
        """Test unregistration from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self):
        """Test unregistration when student is not registered"""
        response = client.delete(
            "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_with_special_characters(self):
        """Test unregistration with URL encoding for activity names with special characters"""
        # Add an activity with special characters and a participant
        activities["Music & Dance"] = {
            "description": "Music and dance performances",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["dancer@mergington.edu"]
        }
        
        response = client.delete(
            "/activities/Music & Dance/unregister?email=dancer@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered dancer@mergington.edu from Music & Dance"


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple operations"""
    
    def test_signup_and_unregister_flow(self):
        """Test complete flow of signing up and then unregistering"""
        email = "testflow@mergington.edu"
        activity = "Drama Club"
        
        # First, signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Then, unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_multiple_signups_different_activities(self):
        """Test student signing up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        response3 = client.post(f"/activities/Drama Club/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]
        assert email in activities_data["Drama Club"]["participants"]
    
    def test_activity_participant_count_tracking(self):
        """Test that participant counts are tracked correctly"""
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        
        # Chess Club should start with 2 participants
        assert len(initial_data["Chess Club"]["participants"]) == 2
        
        # Add a new participant
        client.post("/activities/Chess Club/signup?email=newmember@mergington.edu")
        
        activities_response = client.get("/activities")
        updated_data = activities_response.json()
        
        # Should now have 3 participants
        assert len(updated_data["Chess Club"]["participants"]) == 3
        
        # Remove a participant
        client.delete("/activities/Chess Club/unregister?email=newmember@mergington.edu")
        
        activities_response = client.get("/activities")
        final_data = activities_response.json()
        
        # Should be back to 2 participants
        assert len(final_data["Chess Club"]["participants"]) == 2


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_email_parameter(self):
        """Test with empty email parameter"""
        response = client.post("/activities/Chess Club/signup?email=")
        # Our API accepts empty email (this is actually valid behavior)
        # but we could add validation if needed
        assert response.status_code == 200
    
    def test_missing_email_parameter(self):
        """Test with missing email parameter"""
        response = client.post("/activities/Chess Club/signup")
        # FastAPI should require the email parameter
        assert response.status_code == 422
    
    def test_activity_name_with_spaces(self):
        """Test activity names with spaces are handled correctly"""
        response = client.post("/activities/Chess Club/signup?email=spacestest@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" in data["message"]