"""Test controller."""

import time
from datetime import UTC
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from motor.core import AgnosticDatabase
from odmantic import Model

from fastapi_sdk.controllers import ModelController
from tests.controllers import Account, Project, PublicController, Task
from tests.models import AccountModel
from tests.schemas import AccountCreate, AccountUpdate


@pytest.fixture(autouse=True)
def register_controllers():
    """Register controllers for testing."""
    ModelController.register_controller("Account", Account)
    ModelController.register_controller("Project", Project)
    ModelController.register_controller("Task", Task)


async def fixtures(db_engine: AgnosticDatabase):
    """Re-usable test fictures"""
    # Create two accounts without claims (top-level model)
    account_1 = await Account(db_engine).create({"name": "Account 1"})
    account_2 = await Account(db_engine).create({"name": "Account 2"})

    return account_1, account_2


@pytest.mark.asyncio
async def test_model_controller(db_engine: AgnosticDatabase):
    """Test model controller."""

    # Create two accounts, one for crud test and one for listing
    account_1, account_2 = await fixtures(db_engine)

    assert account_1.uuid
    assert account_1.name == "Account 1"
    assert account_1.created_at
    assert account_1.updated_at

    # Get account
    account_1 = await Account(db_engine).get(
        uuid=account_1.uuid, claims={"account_id": account_1.uuid}
    )
    assert account_1

    # Sleep for 1 seconds to test updated_at
    time.sleep(1)

    # Update account
    account_1 = await Account(db_engine).update(
        uuid=account_1.uuid,
        data={"name": "Account 1 Updated"},
        claims={"account_id": account_1.uuid},
    )

    assert account_1.name == "Account 1 Updated"
    assert account_1.updated_at > account_1.created_at.replace(tzinfo=UTC)

    # List accounts
    accounts = await Account(db_engine).list(claims={"account_id": account_1.uuid})
    assert len(accounts["items"]) == 1
    assert accounts["total"] == 1
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # Test n_per_page functionality
    # Test default n_per_page (25)
    accounts = await Account(db_engine).list(claims={"account_id": account_1.uuid})
    assert len(accounts["items"]) == 1
    assert accounts["total"] == 1
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # Test custom n_per_page
    accounts = await Account(db_engine).list(
        claims={"account_id": account_1.uuid}, n_per_page=10
    )
    assert len(accounts["items"]) == 1
    assert accounts["total"] == 1
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # Test n_per_page exceeding max limit (250)
    accounts = await Account(db_engine).list(
        claims={"account_id": account_1.uuid}, n_per_page=300
    )
    assert len(accounts["items"]) == 1
    assert accounts["total"] == 1
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # Delete account
    account_1 = await Account(db_engine).delete(
        uuid=account_1.uuid, claims={"account_id": account_1.uuid}
    )
    assert account_1.deleted is True

    # Get deleted account
    deleted_account = await Account(db_engine).get(
        uuid=account_1.uuid, claims={"account_id": account_1.uuid}
    )
    assert deleted_account is None

    # Get deleted account with include_deleted=True
    deleted_account = await Account(db_engine).get(
        uuid=account_1.uuid, claims={"account_id": account_1.uuid}, include_deleted=True
    )
    assert deleted_account is not None
    assert deleted_account.deleted is True

    # List deleted accounts
    deleted_accounts = await Account(db_engine).list(
        deleted=True, claims={"account_id": account_1.uuid}
    )
    assert len(deleted_accounts["items"]) == 1
    assert deleted_accounts["items"][0].uuid == account_1.uuid
    assert deleted_accounts["items"][0].deleted is True
    assert deleted_accounts["total"] == 1
    assert deleted_accounts["page"] == 1
    assert deleted_accounts["pages"] == 1

    # Update deleted account
    deleted_account = await Account(db_engine).update(
        uuid=account_1.uuid,
        data={"name": "Account 1 Updated"},
        claims={"account_id": account_1.uuid},
    )
    assert deleted_account is None

    # List accounts with one deleted
    accounts = await Account(db_engine).list(claims={"account_id": account_2.uuid})
    assert len(accounts["items"]) == 1
    assert accounts["items"][0].uuid == account_2.uuid
    assert accounts["total"] == 1
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # Test count method
    # Count all non-deleted accounts
    total_accounts = await Account(db_engine).count(
        claims={"account_id": account_2.uuid}
    )
    assert total_accounts == 1

    # Count deleted accounts
    deleted_count = await Account(db_engine).count(
        deleted=True, claims={"account_id": account_1.uuid}
    )
    assert deleted_count == 1

    # Count with query
    query_count = await Account(db_engine).count(
        query=[{"name": "Account 2"}], claims={"account_id": account_2.uuid}
    )
    assert query_count == 1

    # Undelete account
    undeleted_account = await Account(db_engine).undelete(
        uuid=account_1.uuid, claims={"account_id": account_1.uuid}
    )
    assert undeleted_account is not None
    assert undeleted_account.deleted is False
    assert undeleted_account.uuid == account_1.uuid

    # Count with superuser claims
    superuser_count = await Account(db_engine).count(
        claims={"account_id": account_2.uuid, "roles": ["superuser"]}
    )
    assert superuser_count == 2

    # Verify account is now accessible without include_deleted
    restored_account = await Account(db_engine).get(
        uuid=account_1.uuid, claims={"account_id": account_1.uuid}
    )
    assert restored_account is not None
    assert restored_account.deleted is False

    # Test superuser access
    superuser_claims = {"account_id": account_2.uuid, "roles": ["superuser"]}

    # Superuser can list all accounts
    all_accounts = await Account(db_engine).list(claims=superuser_claims)
    assert len(all_accounts["items"]) == 2
    assert all_accounts["total"] == 2

    # Superuser can get any account
    _account_1 = await Account(db_engine).get(
        uuid=account_1.uuid, claims=superuser_claims
    )
    _account_2 = await Account(db_engine).get(
        uuid=account_2.uuid, claims=superuser_claims
    )
    assert _account_1 is not None
    assert _account_2 is not None

    # Superuser can update any account
    updated_account = await Account(db_engine).update(
        uuid=account_1.uuid,
        data={"name": "Account 1 Superuser Updated"},
        claims=superuser_claims,
    )
    assert updated_account.name == "Account 1 Superuser Updated"

    # Superuser can delete any account
    deleted_account = await Account(db_engine).delete(
        uuid=account_2.uuid, claims=superuser_claims
    )
    assert deleted_account.deleted is True


@pytest.mark.asyncio
async def test_list_options(db_engine: AgnosticDatabase):
    """Test the list options of the controller."""

    # Create two accounts, one for crud test and one for listing
    account_1, account_2 = await fixtures(db_engine)

    # Default listing
    accounts = await Account(db_engine).list(
        claims={"account_id": account_1.uuid, "roles": ["superuser"]}
    )
    assert len(accounts["items"]) == 2
    assert accounts["total"] == 2
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # List with page 2 (Page 1 is the same as default, page 0)
    accounts = await Account(db_engine).list(
        page=2, claims={"account_id": account_1.uuid, "roles": ["superuser"]}
    )
    assert len(accounts["items"]) == 0
    assert accounts["total"] == 2
    assert accounts["page"] == 2
    assert accounts["pages"] == 1

    # List with query
    accounts = await Account(db_engine).list(
        query=[{"name": "Account 1"}],
        claims={"account_id": account_1.uuid, "roles": ["superuser"]},
    )
    assert len(accounts["items"]) == 1
    assert accounts["items"][0].uuid == account_1.uuid
    assert accounts["total"] == 1
    assert accounts["page"] == 1
    assert accounts["pages"] == 1

    # List with order_by
    accounts = await Account(db_engine).list(
        order_by={"name": -1},
        claims={"account_id": account_1.uuid, "roles": ["superuser"]},
    )
    assert len(accounts["items"]) == 2
    assert accounts["items"][0].uuid == account_2.uuid
    assert accounts["items"][1].uuid == account_1.uuid
    assert accounts["total"] == 2
    assert accounts["page"] == 1
    assert accounts["pages"] == 1


@pytest.mark.asyncio
async def test_relationships(db_engine: AgnosticDatabase):
    """Test relationship handling between models."""
    # Create an account
    account = await Account(db_engine).create({"name": "Test Account"})

    # Create a project for this account
    project = await Project(db_engine).create(
        {"name": "Test Project", "account_id": account.uuid},
        claims={"account_id": account.uuid},
    )

    # Create a task for this project
    task = await Task(db_engine).create(
        {
            "name": "Test Task",
            "description": "Test Task",
            "account_id": account.uuid,
            "project_id": project.uuid,
        },
        claims={"account_id": account.uuid},
    )

    # Test getting account with related projects
    account_with_projects = await Account(db_engine).get(
        uuid=account.uuid, include=["projects"], claims={"account_id": account.uuid}
    )
    assert len(account_with_projects.projects) == 1
    assert account_with_projects.projects[0].uuid == project.uuid

    # Test getting project with related account and tasks
    project_with_relations = await Project(db_engine).get(
        uuid=project.uuid,
        include=["account", "tasks"],
        claims={"account_id": account.uuid},
    )
    assert project_with_relations.account.uuid == account.uuid
    assert len(project_with_relations.tasks) == 1
    assert project_with_relations.tasks[0].uuid == task.uuid

    # Test cascade delete
    await Account(db_engine).delete_with_relations(
        uuid=account.uuid, claims={"account_id": account.uuid}
    )

    # Verify everything is deleted
    deleted_project = await Project(db_engine).get(
        uuid=project.uuid, claims={"account_id": account.uuid}
    )
    deleted_task = await Task(db_engine).get(
        uuid=task.uuid, claims={"account_id": account.uuid}
    )
    assert deleted_project is None
    assert deleted_task is None


@pytest.mark.asyncio
class TestOwnership:
    """Test ownership functionality."""

    @pytest.fixture
    def account_claims(self, account):
        """Create test account claims."""
        return {"account_id": account.uuid}

    @pytest.fixture
    def different_account_claims(self):
        """Create claims for a different account."""
        return {"account_id": "acc_456"}

    @pytest.fixture
    def no_account_claims(self):
        """Create claims without account_id."""
        return {"user_id": "user_123"}

    async def test_create_top_level_without_claims(self, db_engine):
        """Test creating a top-level model without claims."""
        controller = Account(db_engine)
        data = {"name": "Test Account"}

        instance = await controller.create(data, claims=None)
        assert instance.name == "Test Account"
        assert instance.uuid

    async def test_create_child_without_claims(self, db_engine):
        """Test creating a child model without claims."""
        controller = Project(db_engine)
        data = {"name": "Test Project", "account_id": "test_acc_123"}

        with pytest.raises(HTTPException) as exc_info:
            await controller.create(data, claims=None)
        assert exc_info.value.status_code == 403
        assert (
            "Claims must be provided when ownership rule is set and allow_public is False"
            in str(exc_info.value.detail)
        )

    async def test_create_with_ownership(self, db_engine, account_claims):
        """Test creating a record with ownership."""
        controller = Project(db_engine)
        data = {"name": "Test project", "account_id": account_claims["account_id"]}

        instance = await controller.create(data, claims=account_claims)
        assert instance.name == "Test project"
        assert instance.account_id == account_claims["account_id"]

    async def test_create_without_claims_no_parent(self, db_engine):
        """
        Test creating a record that has no parent without required claims.
        Record with no parent can not be checked for ownership upon creation.
        """
        controller = Account(db_engine)
        data = {"name": "Test Account"}
        account = await controller.create(data, claims=None)
        assert account.uuid

    async def test_create_without_claims(self, db_engine, no_account_claims):
        """Test creating a record without required claims."""
        controller = Project(db_engine)
        data = {"name": "Test Project", "account_id": "test_acc_123"}

        with pytest.raises(HTTPException) as exc_info:
            await controller.create(data, claims=None)
        assert exc_info.value.status_code == 403
        assert (
            "Claims must be provided when ownership rule is set and allow_public is False"
            in str(exc_info.value.detail)
        )

    async def test_get_with_ownership(self, db_engine, account_claims):
        """Test getting a record owned by the user."""
        controller = Project(db_engine)
        data = {"name": "Test Project", "account_id": account_claims["account_id"]}

        # Create a record
        instance = await controller.create(data, claims=account_claims)

        # Get the record
        retrieved = await controller.get(instance.uuid, claims=account_claims)
        assert retrieved is not None
        assert retrieved.uuid == instance.uuid
        assert retrieved.account_id == account_claims["account_id"]

    async def test_get_without_ownership(
        self, db_engine, account_claims, different_account_claims
    ):
        """Test getting a record not owned by the user."""
        controller = Project(db_engine)
        data = {"name": "Test Project", "account_id": account_claims["account_id"]}

        # Create a record with one account
        instance = await controller.create(data, claims=account_claims)

        # Try to get it with different account
        retrieved = await controller.get(instance.uuid, claims=different_account_claims)
        assert retrieved is None

    async def test_list_with_ownership(
        self, db_engine, account_claims, different_account_claims
    ):
        """Test listing records with ownership filter."""
        controller = Project(db_engine)

        # Create records for different accounts
        data = {"name": "Test Project", "account_id": account_claims["account_id"]}
        await controller.create(data, claims=account_claims)

        data = {
            "name": "Test Project",
            "account_id": different_account_claims["account_id"],
        }
        await controller.create(data, claims=different_account_claims)

        # List records for first account
        result = await controller.list(claims=account_claims)
        assert len(result["items"]) == 1
        assert result["items"][0].account_id == account_claims["account_id"]

        # List records for second account
        result = await controller.list(claims=different_account_claims)
        assert len(result["items"]) == 1
        assert result["items"][0].account_id == different_account_claims["account_id"]

    async def test_update_with_ownership(
        self, db_engine, account_claims, different_account_claims
    ):
        """Test updating records with ownership."""
        controller = Project(db_engine)
        data = {"name": "Test Project", "account_id": account_claims["account_id"]}

        # Create a record
        instance = await controller.create(data, claims=account_claims)

        # Update with correct ownership
        updated = await controller.update(
            instance.uuid,
            {"name": "Updated Project"},
            claims=account_claims,
        )
        assert updated is not None
        assert updated.name == "Updated Project"

        # Try to update with different account
        updated = await controller.update(
            instance.uuid,
            {"name": "Hacked Account"},
            claims=different_account_claims,
        )
        assert updated is None

    async def test_delete_with_ownership(
        self, db_engine, account_claims, different_account_claims
    ):
        """Test deleting records with ownership."""
        controller = Project(db_engine)
        data = {"name": "Test Project", "account_id": account_claims["account_id"]}

        # Create a record
        instance = await controller.create(data, claims=account_claims)

        # Delete with correct ownership
        deleted = await controller.delete(instance.uuid, claims=account_claims)
        assert deleted is not None
        assert deleted.deleted is True

        # Try to delete with different project
        instance = await controller.create(data, claims=account_claims)
        deleted = await controller.delete(
            instance.uuid, claims=different_account_claims
        )
        assert deleted is None

    async def test_public_access(self, db_engine, account_claims, no_account_claims):
        """Test access to public records."""
        controller = PublicController(db_engine)
        data = {"name": "Test Project", "account_id": account_claims["account_id"]}

        # Create a record without claims
        instance = await controller.create(data, claims=no_account_claims)
        assert instance.name == "Test Project"
        assert instance.account_id == account_claims["account_id"]

        # Get the record without claims
        retrieved = await controller.get(instance.uuid, claims=no_account_claims)
        assert retrieved is not None
        assert retrieved.uuid == instance.uuid
        assert retrieved.account_id == account_claims["account_id"]

    async def test_nested_ownership(self, db_engine, account_claims):
        """Test ownership with nested relationships."""
        account_controller = Account(db_engine)
        project_controller = Project(db_engine)

        # Create an account
        account = await account_controller.create(
            {"name": "Test Account"},
            claims=account_claims,
        )

        # Create a project for the account
        project = await project_controller.create(
            {"name": "Test Project", "account_id": account.uuid},
            claims={"account_id": account.uuid},
        )

        # Verify project ownership
        assert project.account_id == account.uuid

        # Try to get project with different account
        different_claims = {"account_id": "acc_456"}
        retrieved = await project_controller.get(project.uuid, claims=different_claims)
        assert retrieved is None

    async def test_create_with_ownership_forbidden(self, db_engine, account_claims):
        """Test creating a record with incorrect ownership value is forbidden."""
        controller = Project(db_engine)
        data = {
            "name": "Test project",
            "account_id": "acc_999",  # Different from the claim value "acc_123"
        }

        with pytest.raises(HTTPException) as exc_info:
            await controller.create(data, claims=account_claims)
        assert exc_info.value.status_code == 403
        assert "Invalid account_id" in str(exc_info.value.detail)

    async def test_create_with_public_access(self, db_engine, account):
        """Test creating a record with public access enabled."""
        controller = PublicController(db_engine)
        data = {"name": "Test Public Item", "account_id": account.uuid}

        instance = await controller.create(data, claims=None)
        assert instance.name == "Test Public Item"

    async def test_get_with_public_access(self, db_engine, account):
        """Test getting a record with public access enabled."""
        controller = PublicController(db_engine)
        data = {"name": "Test Public Item", "account_id": account.uuid}

        # Create a record
        instance = await controller.create(data, claims=None)

        # Get the record without claims
        retrieved = await controller.get(instance.uuid, claims=None)
        assert retrieved is not None
        assert retrieved.uuid == instance.uuid

    async def test_list_with_public_access(self, db_engine, account):
        """Test listing records with public access enabled."""
        controller = PublicController(db_engine)
        data = {"name": "Test Public Item", "account_id": account.uuid}

        # Create a record
        await controller.create(data, claims=None)

        # List records without claims
        result = await controller.list(claims=None)
        assert len(result["items"]) == 1
        assert result["items"][0].name == "Test Public Item"

    async def test_update_with_public_access(self, db_engine, account):
        """Test updating a record with public access enabled."""
        controller = PublicController(db_engine)
        data = {"name": "Test Public Item", "account_id": account.uuid}

        # Create a record
        instance = await controller.create(data, claims=None)

        # Update the record without claims
        updated = await controller.update(
            instance.uuid, {"name": "Updated Item"}, claims=None
        )
        assert updated.name == "Updated Item"

    async def test_delete_with_public_access(self, db_engine, account):
        """Test deleting a record with public access enabled."""
        controller = PublicController(db_engine)
        data = {"name": "Test Public Item", "account_id": account.uuid}

        # Create a record
        instance = await controller.create(data, claims=None)

        # Delete the record without claims
        deleted = await controller.delete(instance.uuid, claims=None)
        assert deleted.deleted is True

    async def test_ownership_with_array_claims(self, db_engine):
        """Test ownership filtering with array-based claims."""
        controller = Project(db_engine)

        # Create multiple accounts
        account_1 = await Account(db_engine).create({"name": "Account 1"})
        account_2 = await Account(db_engine).create({"name": "Account 2"})
        account_3 = await Account(db_engine).create({"name": "Account 3"})

        # Create projects for different accounts
        project_1 = await Project(db_engine).create(
            {"name": "Project 1", "account_id": account_1.uuid},
            claims={"account_id": account_1.uuid},
        )
        project_2 = await Project(db_engine).create(
            {"name": "Project 2", "account_id": account_2.uuid},
            claims={"account_id": account_2.uuid},
        )
        project_3 = await Project(db_engine).create(
            {"name": "Project 3", "account_id": account_3.uuid},
            claims={"account_id": account_3.uuid},
        )

        # Test listing with array claims (should see projects for account_1 and account_2)
        array_claims = {"account_id": [account_1.uuid, account_2.uuid]}
        result = await controller.list(claims=array_claims)

        assert len(result["items"]) == 2
        project_uuids = [p.uuid for p in result["items"]]
        assert project_1.uuid in project_uuids
        assert project_2.uuid in project_uuids
        assert project_3.uuid not in project_uuids

        # Test getting individual projects with array claims
        retrieved_project_1 = await controller.get(project_1.uuid, claims=array_claims)
        retrieved_project_2 = await controller.get(project_2.uuid, claims=array_claims)
        retrieved_project_3 = await controller.get(project_3.uuid, claims=array_claims)

        assert retrieved_project_1 is not None
        assert retrieved_project_2 is not None
        assert retrieved_project_3 is None  # Should not be accessible

        # Test updating with array claims
        updated_project_1 = await controller.update(
            project_1.uuid, {"name": "Updated Project 1"}, claims=array_claims
        )
        assert updated_project_1.name == "Updated Project 1"

        # Try to update project_3 (should fail)
        updated_project_3 = await controller.update(
            project_3.uuid, {"name": "Hacked Project"}, claims=array_claims
        )
        assert updated_project_3 is None

        # Test deleting with array claims
        deleted_project_2 = await controller.delete(project_2.uuid, claims=array_claims)
        assert deleted_project_2.deleted is True

        # Try to delete project_3 (should fail)
        deleted_project_3 = await controller.delete(project_3.uuid, claims=array_claims)
        assert deleted_project_3 is None

        # Test count with array claims
        count = await controller.count(claims=array_claims)
        assert count == 1  # Only project_1 should remain (project_2 was deleted)

        # Test creating with array claims
        new_project = await controller.create(
            {"name": "New Project", "account_id": account_1.uuid}, claims=array_claims
        )
        assert new_project.name == "New Project"
        assert new_project.account_id == account_1.uuid

        # Try to create with account_3 (should fail)
        with pytest.raises(HTTPException) as exc_info:
            await controller.create(
                {"name": "Unauthorized Project", "account_id": account_3.uuid},
                claims=array_claims,
            )
        assert exc_info.value.status_code == 403
        assert "Invalid account_id" in str(exc_info.value.detail)

    async def test_ownership_with_single_vs_array_claims(self, db_engine):
        """Test that single value claims and array claims work consistently."""
        controller = Project(db_engine)

        # Create an account
        account = await Account(db_engine).create({"name": "Test Account"})

        # Create a project
        project = await Project(db_engine).create(
            {"name": "Test Project", "account_id": account.uuid},
            claims={"account_id": account.uuid},
        )

        # Test with single value claim
        single_claim = {"account_id": account.uuid}
        result_single = await controller.list(claims=single_claim)
        assert len(result_single["items"]) == 1
        assert result_single["items"][0].uuid == project.uuid

        # Test with array containing the same value
        array_claim = {"account_id": [account.uuid]}
        result_array = await controller.list(claims=array_claim)
        assert len(result_array["items"]) == 1
        assert result_array["items"][0].uuid == project.uuid

        # Both should return the same result
        assert result_single["total"] == result_array["total"]
        assert result_single["items"][0].uuid == result_array["items"][0].uuid

    async def test_ownership_with_empty_array_claims(self, db_engine):
        """Test ownership filtering with empty array claims."""
        controller = Project(db_engine)

        # Create an account and project
        account = await Account(db_engine).create({"name": "Test Account"})
        project = await Project(db_engine).create(
            {"name": "Test Project", "account_id": account.uuid},
            claims={"account_id": account.uuid},
        )

        # Test with empty array claim
        empty_array_claim = {"account_id": []}

        # Try to create with account_3 (should fail)
        with pytest.raises(HTTPException) as exc_info:
            # Should not be able to access any projects
            await controller.list(claims=empty_array_claim)
        assert exc_info.value.status_code == 403
        assert "Missing required claim: account_id" in str(exc_info.value.detail)

        # Should not be able to get the project
        with pytest.raises(HTTPException) as exc_info:
            await controller.get(project.uuid, claims=empty_array_claim)
        assert exc_info.value.status_code == 403
        assert "Missing required claim: account_id" in str(exc_info.value.detail)

        # Should not be able to update the project
        with pytest.raises(HTTPException) as exc_info:
            await controller.update(
                project.uuid, {"name": "Updated"}, claims=empty_array_claim
            )
        assert exc_info.value.status_code == 403
        assert "Missing required claim: account_id" in str(exc_info.value.detail)

        # Should not be able to delete the project
        with pytest.raises(HTTPException) as exc_info:
            await controller.delete(project.uuid, claims=empty_array_claim)
        assert exc_info.value.status_code == 403
        assert "Missing required claim: account_id" in str(exc_info.value.detail)

        # Count should be 0
        with pytest.raises(HTTPException) as exc_info:
            await controller.count(claims=empty_array_claim)
        assert exc_info.value.status_code == 403
        assert "Missing required claim: account_id" in str(exc_info.value.detail)

    async def test_ownership_with_mixed_array_claims(self, db_engine):
        """Test ownership filtering with mixed data types in array claims."""
        controller = Project(db_engine)

        # Create accounts with different ID types
        account_1 = await Account(db_engine).create({"name": "Account 1"})
        account_2 = await Account(db_engine).create({"name": "Account 2"})

        # Create projects
        project_1 = await Project(db_engine).create(
            {"name": "Project 1", "account_id": account_1.uuid},
            claims={"account_id": account_1.uuid},
        )
        project_2 = await Project(db_engine).create(
            {"name": "Project 2", "account_id": account_2.uuid},
            claims={"account_id": account_2.uuid},
        )

        # Test with array containing both account IDs
        mixed_claims = {"account_id": [account_1.uuid, account_2.uuid]}
        result = await controller.list(claims=mixed_claims)

        assert len(result["items"]) == 2
        project_uuids = [p.uuid for p in result["items"]]
        assert project_1.uuid in project_uuids
        assert project_2.uuid in project_uuids

    async def test_ownership_with_user_query_conflict(self, db_engine):
        """Test that ownership filtering works correctly with user-provided queries."""
        controller = Project(db_engine)

        # Create multiple accounts
        account_1 = await Account(db_engine).create({"name": "Account 1"})
        account_2 = await Account(db_engine).create({"name": "Account 2"})
        account_3 = await Account(db_engine).create({"name": "Account 3"})

        # Create projects for different accounts
        project_1 = await Project(db_engine).create(
            {"name": "Project 1", "account_id": account_1.uuid},
            claims={"account_id": account_1.uuid},
        )
        project_2 = await Project(db_engine).create(
            {"name": "Project 2", "account_id": account_2.uuid},
            claims={"account_id": account_2.uuid},
        )
        project_3 = await Project(db_engine).create(
            {"name": "Project 3", "account_id": account_3.uuid},
            claims={"account_id": account_3.uuid},
        )

        # User has access to account_1 and account_2
        array_claims = {"account_id": [account_1.uuid, account_2.uuid]}

        # Test 1: List all projects (should return projects for account_1 and account_2)
        result = await controller.list(claims=array_claims)
        assert len(result["items"]) == 2
        project_uuids = [p.uuid for p in result["items"]]
        assert project_1.uuid in project_uuids
        assert project_2.uuid in project_uuids
        assert project_3.uuid not in project_uuids

        # Test 2: Filter for specific account that user has access to
        result = await controller.list(
            query=[{"account_id": account_1.uuid}], claims=array_claims
        )
        assert len(result["items"]) == 1
        assert result["items"][0].uuid == project_1.uuid

        # Test 3: Filter for specific account that user has access to (account_2)
        result = await controller.list(
            query=[{"account_id": account_2.uuid}], claims=array_claims
        )
        assert len(result["items"]) == 1
        assert result["items"][0].uuid == project_2.uuid

        # Test 4: Try to filter for account user doesn't have access to (should fail)
        with pytest.raises(HTTPException) as exc_info:
            await controller.list(
                query=[{"account_id": account_3.uuid}], claims=array_claims
            )
        assert exc_info.value.status_code == 403
        assert "Access denied: account_id not in your allowed values" in str(
            exc_info.value.detail
        )

        # Test 5: Filter with array query that intersects with ownership
        result = await controller.list(
            query=[{"account_id": {"$in": [account_1.uuid, account_3.uuid]}}],
            claims=array_claims,
        )
        # Should only return project_1 (intersection of user query and ownership)
        assert len(result["items"]) == 1
        assert result["items"][0].uuid == project_1.uuid

        # Test 6: Filter with array query that has no intersection (should fail)
        with pytest.raises(HTTPException) as exc_info:
            await controller.list(
                query=[{"account_id": {"$in": [account_3.uuid]}}], claims=array_claims
            )
        assert exc_info.value.status_code == 403
        assert "Access denied: account_id not in your allowed values" in str(
            exc_info.value.detail
        )

        # Test 7: Filter with array query that is subset of ownership
        result = await controller.list(
            query=[{"account_id": {"$in": [account_1.uuid, account_2.uuid]}}],
            claims=array_claims,
        )
        # Should return both projects (full intersection)
        assert len(result["items"]) == 2
        project_uuids = [p.uuid for p in result["items"]]
        assert project_1.uuid in project_uuids
        assert project_2.uuid in project_uuids

        # Test 8: Count with specific account filter
        count = await controller.count(
            query=[{"account_id": account_1.uuid}], claims=array_claims
        )
        assert count == 1

        # Test 9: Count with unauthorized account filter (should fail)
        with pytest.raises(HTTPException) as exc_info:
            await controller.count(
                query=[{"account_id": account_3.uuid}], claims=array_claims
            )
        assert exc_info.value.status_code == 403

    async def test_ownership_with_single_value_claims_and_query(self, db_engine):
        """Test ownership filtering with single value claims and user queries."""
        controller = Project(db_engine)

        # Create accounts
        account_1 = await Account(db_engine).create({"name": "Account 1"})
        account_2 = await Account(db_engine).create({"name": "Account 2"})

        # Create projects
        project_1 = await Project(db_engine).create(
            {"name": "Project 1", "account_id": account_1.uuid},
            claims={"account_id": account_1.uuid},
        )
        project_2 = await Project(db_engine).create(
            {"name": "Project 2", "account_id": account_2.uuid},
            claims={"account_id": account_2.uuid},
        )

        # User has access to only account_1
        single_claims = {"account_id": account_1.uuid}

        # Test 1: List all projects (should return only project_1)
        result = await controller.list(claims=single_claims)
        assert len(result["items"]) == 1
        assert result["items"][0].uuid == project_1.uuid

        # Test 2: Filter for the account user has access to
        result = await controller.list(
            query=[{"account_id": account_1.uuid}], claims=single_claims
        )
        assert len(result["items"]) == 1
        assert result["items"][0].uuid == project_1.uuid

        # Test 3: Try to filter for account user doesn't have access to (should fail)
        with pytest.raises(HTTPException) as exc_info:
            await controller.list(
                query=[{"account_id": account_2.uuid}], claims=single_claims
            )
        assert exc_info.value.status_code == 403
        assert "Access denied: account_id not in your allowed values" in str(
            exc_info.value.detail
        )


@pytest.mark.asyncio
async def test_list_with_relations(db_engine: AgnosticDatabase):
    """Test listing models with included relations."""

    # Create test data
    account = await Account(db_engine).create({"name": "Test Account"})
    account_claims = {"account_id": account.uuid}
    project = await Project(db_engine).create(
        {"name": "Test Project", "account_id": account.uuid},
        claims=account_claims,
    )
    task = await Task(db_engine).create(
        {
            "name": "Test Task",
            "description": "Test Task Description",
            "account_id": account.uuid,
            "project_id": project.uuid,
        },
        claims=account_claims,
    )

    # Test listing accounts with projects included
    result = await Account(db_engine).list(include=["projects"], claims=account_claims)
    assert result["total"] >= 1
    account_with_projects = next(
        (a for a in result["items"] if a.uuid == account.uuid), None
    )
    assert account_with_projects is not None
    assert hasattr(account_with_projects, "projects")
    assert len(account_with_projects.projects) >= 1
    assert any(p.uuid == project.uuid for p in account_with_projects.projects)

    # Test listing projects with tasks included
    result = await Project(db_engine).list(include=["tasks"], claims=account_claims)
    assert result["total"] >= 1
    project_with_tasks = next(
        (p for p in result["items"] if p.uuid == project.uuid), None
    )
    assert project_with_tasks is not None
    assert hasattr(project_with_tasks, "tasks")
    assert len(project_with_tasks.tasks) >= 1
    assert any(t.uuid == task.uuid for t in project_with_tasks.tasks)

    # Test listing with multiple relations
    result = await Project(db_engine).list(
        include=["tasks", "account"], claims=account_claims
    )
    assert result["total"] >= 1
    project_with_relations = next(
        (p for p in result["items"] if p.uuid == project.uuid), None
    )
    assert project_with_relations is not None
    assert hasattr(project_with_relations, "account")
    assert hasattr(project_with_relations, "tasks")
    assert len(project_with_relations.tasks) >= 1
    assert any(t.uuid == task.uuid for t in project_with_relations.tasks)

    # Test listing with non-existent relation
    result = await Account(db_engine).list(
        include=["non_existent"], claims=account_claims
    )
    assert result["total"] >= 1
    account = next((a for a in result["items"] if a.uuid == account.uuid), None)
    assert account is not None


@pytest.mark.asyncio
async def test_task_with_assignees(db_engine: AgnosticDatabase):
    """Test creating and updating tasks with assignees."""
    # Create an account first
    account = await Account(db_engine).create({"name": "Test Account"})
    project = await Project(db_engine).create(
        {
            "name": "Test Project",
            "account_id": account.uuid,
        },
        claims={"account_id": account.uuid},
    )

    # Create a task with assignees
    task_data = {
        "name": "Test Task",
        "description": "A test task with assignees",
        "project_id": project.uuid,
        "account_id": account.uuid,
        "assignees": [
            {
                "uuid": "asn_123",
                "name": "John Doe",
                "email": "john@example.com",
            },
            {
                "uuid": "asn_456",
                "name": "Jane Smith",
                "email": "jane@example.com",
            },
        ],
    }

    # Create the task
    task = await Task(db_engine).create(
        task_data,
        claims={"account_id": account.uuid},
    )

    assert task is not None
    assert task.name == "Test Task"
    assert len(task.assignees) == 2
    assert task.assignees[0].name == "John Doe"
    assert task.assignees[0].email == "john@example.com"
    assert task.assignees[1].name == "Jane Smith"
    assert task.assignees[1].email == "jane@example.com"

    # Update the task with new assignees
    updated_task_data = {
        "name": "Updated Task",
        "assignees": [
            {
                "uuid": "asn_789",
                "name": "Bob Wilson",
                "email": "bob@example.com",
            },
        ],
    }

    updated_task = await Task(db_engine).update(
        task.uuid,
        updated_task_data,
        claims={"account_id": account.uuid},
    )

    assert updated_task is not None
    assert updated_task.name == "Updated Task"
    assert len(updated_task.assignees) == 1
    assert updated_task.assignees[0].name == "Bob Wilson"
    assert updated_task.assignees[0].email == "bob@example.com"

    # Test updating with empty assignees list
    empty_assignees_data = {
        "assignees": [],
    }

    task_with_empty_assignees = await Task(db_engine).update(
        task.uuid,
        empty_assignees_data,
        claims={"account_id": account.uuid},
    )

    assert task_with_empty_assignees is not None
    assert len(task_with_empty_assignees.assignees) == 0


@pytest.mark.asyncio
async def test_get_with_include(db_engine: AgnosticDatabase):
    """Test getting a model with included relationships."""
    # Create test data
    account = await Account(db_engine).create({"name": "Test Account"})
    account_claims = {"account_id": account.uuid}

    # Create projects for this account
    project_1 = await Project(db_engine).create(
        {"name": "Project 1", "account_id": account.uuid},
        claims=account_claims,
    )
    project_2 = await Project(db_engine).create(
        {"name": "Project 2", "account_id": account.uuid},
        claims=account_claims,
    )

    # Create tasks for the first project
    task_1 = await Task(db_engine).create(
        {
            "name": "Task 1",
            "description": "First task",
            "account_id": account.uuid,
            "project_id": project_1.uuid,
        },
        claims=account_claims,
    )
    task_2 = await Task(db_engine).create(
        {
            "name": "Task 2",
            "description": "Second task",
            "account_id": account.uuid,
            "project_id": project_1.uuid,
        },
        claims=account_claims,
    )

    # Test getting account with projects (one-to-many)
    account_with_projects = await Account(db_engine).get(
        uuid=account.uuid, include=["projects"], claims=account_claims
    )
    assert account_with_projects is not None
    assert hasattr(account_with_projects, "projects")
    assert len(account_with_projects.projects) == 2
    project_uuids = [p.uuid for p in account_with_projects.projects]
    assert project_1.uuid in project_uuids
    assert project_2.uuid in project_uuids

    # Test getting project with account (many-to-one) and tasks (one-to-many)
    project_with_relations = await Project(db_engine).get(
        uuid=project_1.uuid, include=["account", "tasks"], claims=account_claims
    )
    assert project_with_relations is not None
    assert hasattr(project_with_relations, "account")
    assert hasattr(project_with_relations, "tasks")

    # Verify many-to-one relationship (account)
    assert project_with_relations.account.uuid == account.uuid
    assert project_with_relations.account.name == "Test Account"

    # Verify one-to-many relationship (tasks)
    assert len(project_with_relations.tasks) == 2
    task_uuids = [t.uuid for t in project_with_relations.tasks]
    assert task_1.uuid in task_uuids
    assert task_2.uuid in task_uuids

    # Test getting task with project (many-to-one)
    task_with_project = await Task(db_engine).get(
        uuid=task_1.uuid, include=["project"], claims=account_claims
    )
    assert task_with_project is not None
    assert hasattr(task_with_project, "project")
    assert task_with_project.project.uuid == project_1.uuid
    assert task_with_project.project.name == "Project 1"

    # Test getting with non-existent relationship
    account_with_invalid = await Account(db_engine).get(
        uuid=account.uuid, include=["non_existent_relation"], claims=account_claims
    )
    assert account_with_invalid is not None
    assert not hasattr(account_with_invalid, "non_existent_relation")

    # Test getting without include parameter (should work normally)
    account_normal = await Account(db_engine).get(
        uuid=account.uuid, claims=account_claims
    )
    assert account_normal is not None
    assert account_normal.projects is None


@pytest.mark.asyncio
async def test_one_based_pagination(db_engine: AgnosticDatabase):
    """Test that pagination uses 1-based indexing."""
    # Create an account
    account = await Account(db_engine).create({"name": "Test Account"})
    account_claims = {"account_id": account.uuid}

    # Create multiple projects for this account
    projects = []
    for i in range(5):
        project = await Project(db_engine).create(
            {"name": f"Project {i}", "account_id": account.uuid},
            claims=account_claims,
        )
        projects.append(project)

    # Add task for each project
    for project in projects:
        await Task(db_engine).create(
            {
                "name": f"Task {project.name}",
                "project_id": project.uuid,
                "account_id": account.uuid,
            },
            claims=account_claims,
        )

    # Test that page 0 raises an error
    with pytest.raises(ValueError, match="Page number must be 1 or greater"):
        await Project(db_engine).list(page=0, claims=account_claims)

    # Test that page -1 raises an error
    with pytest.raises(ValueError, match="Page number must be 1 or greater"):
        await Project(db_engine).list(page=-1, claims=account_claims)

    # Test first page (page 1)
    result_page_1 = await Project(db_engine).list(
        page=1, n_per_page=2, claims=account_claims
    )

    assert result_page_1["total"] == 5
    assert len(result_page_1["items"]) == 2
    assert result_page_1["page"] == 1
    assert result_page_1["pages"] == 3  # 5 items / 2 per page = 3 pages
    assert result_page_1["size"] == 2

    # Test second page (page 2)
    result_page_2 = await Project(db_engine).list(
        page=2, n_per_page=2, claims=account_claims
    )

    assert result_page_2["total"] == 5
    assert len(result_page_2["items"]) == 2
    assert result_page_2["page"] == 2
    assert result_page_2["pages"] == 3
    assert result_page_2["size"] == 2

    # Test third page (page 3) - should have 1 item
    result_page_3 = await Project(db_engine).list(
        page=3, n_per_page=2, claims=account_claims
    )

    assert result_page_3["total"] == 5
    assert len(result_page_3["items"]) == 1
    assert result_page_3["page"] == 3
    assert result_page_3["pages"] == 3
    assert result_page_3["size"] == 1

    # Verify that all projects are returned across all pages
    all_project_uuids = set()
    for result in [result_page_1, result_page_2, result_page_3]:
        for project in result["items"]:
            all_project_uuids.add(project.name)

    expected_uuids = {project.name for project in projects}
    assert all_project_uuids == expected_uuids

    # Test default page (should be 1)
    result_default = await Project(db_engine).list(claims=account_claims)
    assert result_default["page"] == 1


@pytest.mark.asyncio
class TestControllerHooks:
    """Test controller hooks functionality."""

    class HookTestController(ModelController):
        """Test controller with hook implementations."""

        model = AccountModel
        schema_create = AccountCreate
        schema_update = AccountUpdate

        def __init__(self, db_engine):
            """Initialize with mock notification function."""
            super().__init__(db_engine)
            self.notify = AsyncMock()

        async def before_create(
            self, data_dict: dict, claims: Optional[Dict[str, Any]] = None
        ) -> dict:
            """Add extra field before creation."""
            if claims and "user_id" in claims:
                data_dict["created_by"] = claims["user_id"]
            return data_dict

        async def after_create(
            self, obj: Model, claims: Optional[dict] = None
        ) -> Model:
            """Add after creation send notification."""
            await self.notify(
                event_type="account_created", account_id=obj.uuid, account_name=obj.name
            )
            return obj

        async def before_update(
            self, data_dict: dict, claims: Optional[Dict[str, Any]] = None
        ) -> dict:
            """Add extra field before update."""
            if claims and "user_id" in claims:
                data_dict["updated_by"] = claims["user_id"]
            return data_dict

        async def after_update(
            self, obj: Model, claims: Optional[dict] = None
        ) -> Model:
            """Add after update send notification."""
            await self.notify(
                event_type="account_updated", account_id=obj.uuid, account_name=obj.name
            )
            return obj

    async def test_create_hooks(self, db_engine: AgnosticDatabase):
        """Test before_create and after_create hooks."""
        controller = self.HookTestController(db_engine)
        claims = {"user_id": "test_user"}

        # Create a model with hooks
        model = await controller.create({"name": "Test Account"}, claims=claims)

        # Verify before_create hook effects
        assert model.created_by == "test_user"

        # Verify notification was sent
        controller.notify.assert_called_once_with(
            event_type="account_created",
            account_id=model.uuid,
            account_name="Test Account",
        )

    async def test_update_hooks(self, db_engine: AgnosticDatabase):
        """Test before_update and after_update hooks."""
        controller = self.HookTestController(db_engine)
        claims = {"user_id": "test_user"}

        # First create a model
        model = await controller.create({"name": "Test Account"}, claims=claims)

        # Reset mock to clear create notification
        controller.notify.reset_mock()

        # Update the model with hooks
        updated_model = await controller.update(
            model.uuid, {"name": "Updated Account"}, claims=claims
        )

        # Verify before_update hook effects
        assert updated_model.updated_by == "test_user"

        # Verify notification was sent
        controller.notify.assert_called_once_with(
            event_type="account_updated",
            account_id=updated_model.uuid,
            account_name="Updated Account",
        )

    async def test_hooks_without_claims(self, db_engine: AgnosticDatabase):
        """Test hooks behavior without claims."""
        controller = self.HookTestController(db_engine)

        # Create a model without claims
        model = await controller.create({"name": "Test Account"})

        # Verify before_create hook effects without claims
        assert model.created_by is None

        # Verify create notification was sent
        controller.notify.assert_called_once_with(
            event_type="account_created",
            account_id=model.uuid,
            account_name="Test Account",
        )

        # Reset mock to clear create notification
        controller.notify.reset_mock()

        # Update without claims
        updated_model = await controller.update(model.uuid, {"name": "Updated Account"})

        # Verify before_update hook effects without claims
        assert updated_model.updated_by is None

        # Verify update notification was sent
        controller.notify.assert_called_once_with(
            event_type="account_updated",
            account_id=updated_model.uuid,
            account_name="Updated Account",
        )
