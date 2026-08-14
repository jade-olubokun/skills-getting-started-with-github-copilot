"""
Tests for the Mergington High School Activities API
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Should return a dict of activities
        assert isinstance(activities, dict)
        # Should contain expected activities
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_structure_is_valid(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_participant_counts_are_correct(self, client):
        """Test that participant counts match the data"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Programming Class should have 2 participants
        assert len(activities["Programming Class"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_succeeds(self, client):
        """Test successful signup for a new student"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "new_student@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_updates_participant_list(self, client):
        """Test that signup adds student to participants list"""
        new_email = "another_student@mergington.edu"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Signup new student
        client.post(
            "/activities/Chess Club/signup",
            params={"email": new_email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert new_email in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student_returns_400(self, client):
        """Test signup for already registered student returns 400"""
        # Try to signup someone already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for POST /activities/{activity_name}/remove endpoint"""

    def test_remove_participant_succeeds(self, client):
        """Test successful removal of a participant"""
        response = client.post(
            "/activities/Chess Club/remove",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_updates_participant_list(self, client):
        """Test that removal removes student from participants list"""
        email_to_remove = "michael@mergington.edu"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Remove participant
        client.post(
            "/activities/Chess Club/remove",
            params={"email": email_to_remove}
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email_to_remove not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test removal from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/remove",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonparticipant_returns_400(self, client):
        """Test removal of non-participant returns 400"""
        response = client.post(
            "/activities/Chess Club/remove",
            params={"email": "not_in_club@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
