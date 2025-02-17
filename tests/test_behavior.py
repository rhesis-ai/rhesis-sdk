import pytest
from rhesis.entities import Behavior, Status
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def test_status():
    """Fixture that creates and returns a test status"""
    # Try to find existing test status
    statuses = Status.all()
    test_status = next((s for s in statuses if s["name"] == "Test"), None)

    if test_status:
        yield test_status
        return  # No cleanup needed for existing status

    # Create new test status if it doesn't exist
    status = Status(name="Test", description="Test status").save()
    yield status
    # Cleanup: delete the status after test only if we created it
    try:
        Status.from_id(status["id"]).delete(status["id"])
    except (ValueError, KeyError):  # For not found or invalid ID
        pass


@pytest.fixture
def test_behavior(test_status):
    """Fixture that creates and returns a test behavior"""
    behavior = Behavior(
        name="Test Behavior",
        description="This is a test behavior",
        status_id=test_status["id"],
    ).save()

    # Verify the save was successful
    assert behavior is not None, "Failed to create test behavior"
    assert "id" in behavior, "Created behavior missing ID"

    yield behavior
    # Cleanup: delete the behavior after test
    try:
        if Behavior.exists(behavior["id"]):
            Behavior.from_id(behavior["id"]).delete(behavior["id"])
    except (ValueError, KeyError):  # For not found or invalid ID
        pass


def assert_valid_behavior_fields(behavior):
    """Helper function to check behavior fields"""
    assert "id" in behavior
    assert behavior["name"] == "Test Behavior"
    assert behavior["description"] == "This is a test behavior"
    assert "status_id" in behavior


def test_create_behavior(test_behavior):
    assert_valid_behavior_fields(test_behavior)


def test_read_behavior_by_id(test_behavior):
    behavior = Behavior.from_id(test_behavior["id"])
    assert_valid_behavior_fields(behavior.fields)


def test_read_behaviors(test_behavior):
    behaviors = Behavior.all()
    assert isinstance(behaviors, list)
    # Find our test behavior in the list
    test_behavior_from_list = next(
        (b for b in behaviors if b["id"] == test_behavior["id"]), None
    )
    assert test_behavior_from_list is not None
    assert_valid_behavior_fields(test_behavior_from_list)


def test_update_behavior(test_behavior, test_status):
    behavior = Behavior.from_id(test_behavior["id"])
    behavior.fields["status_id"] = test_status["id"]
    updated_behavior = behavior.save()
    assert updated_behavior["status_id"] == test_status["id"]


def test_delete_behavior(test_behavior):
    behavior_id = test_behavior["id"]
    behavior = Behavior.from_id(behavior_id)
    behavior.delete(behavior_id)

    # Check if behavior still exists
    assert not Behavior.exists(behavior_id), "Behavior should have been deleted"
