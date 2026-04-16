"""
Unit tests for the High School Management System API using AAA pattern.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [status.HTTP_302_FOUND, status.HTTP_307_TEMPORARY_REDIRECT]
        assert response.headers.get("location") == expected_redirect_url


class TestGetActivities:
    """Tests for retrieving activities."""

    def test_get_all_activities_returns_complete_list(self, client):
        # Arrange
        expected_activity_count = 9  # Based on the current activities data

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == expected_activity_count

        # Verify structure of first activity
        chess_club = activities.get("Chess Club")
        assert chess_club is not None
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_all_expected_activities(self, client):
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Music Ensemble", "Debate Team", "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        activities = response.json()
        assert set(expected_activities) == set(activities.keys())


class TestSignupForActivity:
    """Tests for signing up students for activities."""

    def test_signup_valid_student_for_valid_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        new_email = "new_student@mergington.edu"

        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "message" in response_data
        assert new_email in response_data["message"]
        assert activity_name in response_data["message"]

        # Verify participant was added
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_participants + 1
        assert new_email in updated_participants

    def test_signup_duplicate_email_returns_bad_request(self, client):
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already exists in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "detail" in response_data
        assert "already signed up" in response_data["detail"].lower()

    def test_signup_for_nonexistent_activity_returns_not_found(self, client):
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "detail" in response_data
        assert "not found" in response_data["detail"].lower()


class TestRemoveParticipant:
    """Tests for removing participants from activities."""

    def test_remove_existing_participant_from_activity(self, client):
        # Arrange
        activity_name = "Programming Class"
        email_to_remove = "emma@mergington.edu"  # Exists in Programming Class

        # Get initial participant count
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)
        assert email_to_remove in initial_participants

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email_to_remove}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "message" in response_data
        assert email_to_remove in response_data["message"]
        assert activity_name in response_data["message"]

        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert len(updated_participants) == initial_count - 1
        assert email_to_remove not in updated_participants

    def test_remove_participant_from_nonexistent_activity_returns_not_found(self, client):
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/participants/{email}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "detail" in response_data

    def test_remove_nonexistent_participant_from_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{nonexistent_email}")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        response_data = response.json()
        assert "detail" in response_data
        assert "not found" in response_data["detail"].lower()


class TestStaticFiles:
    """Tests for static file serving."""

    def test_static_index_html_is_served(self, client):
        # Arrange
        static_file_path = "/static/index.html"

        # Act
        response = client.get(static_file_path)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")
        assert len(response.text) > 0  # Should have content