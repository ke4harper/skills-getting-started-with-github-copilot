"""Tests for the activities API endpoints"""
import pytest


class TestGetActivities:
    """Test the /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Volleyball" in data
        assert "Basketball" in data
        assert "Art Club" in data
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
    
    def test_initial_participants(self, client, reset_activities):
        """Test that initial participants are loaded correctly"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Volleyball"]["participants"]
        assert "james@mergington.edu" in data["Basketball"]["participants"]
        assert len(data["Music Ensemble"]["participants"]) == 2


class TestSignup:
    """Test the signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Volleyball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        client.post("/activities/Volleyball/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Volleyball"]["participants"]
        assert "newstudent@mergington.edu" in participants
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test that already registered student gets error"""
        response = client.post(
            "/activities/Volleyball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_full(self, client, reset_activities):
        """Test signup fails when activity is full"""
        # Get the Robotics Team which has max_participants=10 and 2 current participants
        # Add 8 more participants to fill it
        for i in range(8):
            client.post(
                f"/activities/Robotics Team/signup?email=student{i}@mergington.edu"
            )
        
        # Next signup should fail
        response = client.post(
            "/activities/Robotics Team/signup?email=nextStudent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"].lower()


class TestUnregister:
    """Test the unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregister from an activity"""
        response = client.post(
            "/activities/Volleyball/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "alex@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.post("/activities/Volleyball/unregister?email=alex@mergington.edu")
        
        response = client.get("/activities")
        participants = response.json()["Volleyball"]["participants"]
        assert "alex@mergington.edu" not in participants
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test that unregistering unregistered student gets error"""
        response = client.post(
            "/activities/Volleyball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_and_signup_again(self, client, reset_activities):
        """Test that student can signup again after unregistering"""
        # Unregister
        client.post("/activities/Volleyball/unregister?email=alex@mergington.edu")
        
        # Try to signup again
        response = client.post(
            "/activities/Volleyball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant is registered
        response = client.get("/activities")
        participants = response.json()["Volleyball"]["participants"]
        assert "alex@mergington.edu" in participants


class TestRoot:
    """Test the root endpoint"""
    
    def test_root_redirects(self, client, reset_activities):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
