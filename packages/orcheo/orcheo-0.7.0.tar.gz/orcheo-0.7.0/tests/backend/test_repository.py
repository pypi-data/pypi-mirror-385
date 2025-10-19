"""Unit tests for the in-memory workflow repository implementation."""

from __future__ import annotations
import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4
import pytest
import pytest_asyncio
from orcheo.models.workflow import CredentialHealthStatus
from orcheo.triggers.cron import CronTriggerConfig
from orcheo.triggers.manual import ManualDispatchItem, ManualDispatchRequest
from orcheo.triggers.retry import RetryPolicyConfig
from orcheo.triggers.webhook import WebhookTriggerConfig
from orcheo.vault.oauth import CredentialHealthReport, CredentialHealthResult
from orcheo_backend.app.repository import (
    InMemoryWorkflowRepository,
    RepositoryError,
    SqliteWorkflowRepository,
    VersionDiff,
    WorkflowNotFoundError,
    WorkflowRepository,
    WorkflowRunNotFoundError,
    WorkflowVersionNotFoundError,
)


class StubCredentialService:
    """Test double that simulates credential health responses."""

    def __init__(self) -> None:
        self.unhealthy_workflows: set[UUID] = set()
        self.checked_workflows: list[UUID] = []

    def mark_unhealthy(self, workflow_id: UUID) -> None:
        self.unhealthy_workflows.add(workflow_id)

    def is_workflow_healthy(self, workflow_id: UUID) -> bool:
        return True

    def get_report(
        self, workflow_id: UUID
    ) -> CredentialHealthReport | None:  # pragma: no cover - unused
        return None

    async def ensure_workflow_health(
        self, workflow_id: UUID, *, actor: str | None = None
    ) -> CredentialHealthReport:
        self.checked_workflows.append(workflow_id)
        status = (
            CredentialHealthStatus.UNHEALTHY
            if workflow_id in self.unhealthy_workflows
            else CredentialHealthStatus.HEALTHY
        )
        result = CredentialHealthResult(
            credential_id=uuid4(),
            name="stub",
            provider="stub",
            status=status,
            last_checked_at=datetime.now(tz=UTC),
            failure_reason=None
            if status is CredentialHealthStatus.HEALTHY
            else "invalid",
        )
        return CredentialHealthReport(
            workflow_id=workflow_id,
            results=[result],
            checked_at=datetime.now(tz=UTC),
        )


async def _remove_version(repository: WorkflowRepository, version_id: UUID) -> None:
    """Remove a workflow version for backend-specific implementations."""

    if isinstance(repository, InMemoryWorkflowRepository):
        repository._versions.pop(version_id, None)
        for versions in repository._workflow_versions.values():
            if version_id in versions:
                versions.remove(version_id)
        repository._version_runs.pop(version_id, None)
        return

    if isinstance(repository, SqliteWorkflowRepository):
        async with repository._connection() as conn:  # type: ignore[attr-defined]
            await conn.execute(
                "DELETE FROM workflow_versions WHERE id = ?", (str(version_id),)
            )
            await conn.execute(
                "DELETE FROM workflow_runs WHERE workflow_version_id = ?",
                (str(version_id),),
            )
        return

    raise AssertionError(f"Unsupported repository type: {type(repository)!r}")


@pytest_asyncio.fixture(params=["memory", "sqlite"])
async def repository(
    request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
) -> AsyncIterator[WorkflowRepository]:
    """Return a repository instance backed by the configured backend."""

    if request.param == "memory":
        repo: WorkflowRepository = InMemoryWorkflowRepository()
    else:
        db_path = tmp_path_factory.mktemp("repo") / "workflows.sqlite"
        repo = SqliteWorkflowRepository(db_path)

    try:
        yield repo
    finally:
        await repo.reset()


@pytest.mark.asyncio()
async def test_create_and_list_workflows(repository: WorkflowRepository) -> None:
    """Workflows can be created and listed with deep copies returned."""

    created = await repository.create_workflow(
        name="Test Flow",
        slug=None,
        description="Example workflow",
        tags=["alpha"],
        actor="tester",
    )

    workflows = await repository.list_workflows()
    assert len(workflows) == 1
    assert workflows[0].id == created.id
    assert workflows[0].slug == "test-flow"

    # Returned instances must be detached copies.
    workflows[0].name = "mutated"
    fresh = await repository.get_workflow(created.id)
    assert fresh.name == "Test Flow"


@pytest.mark.asyncio()
async def test_update_and_archive_workflow(
    repository: WorkflowRepository,
) -> None:
    """Updating a workflow touches each branch of metadata normalization."""

    created = await repository.create_workflow(
        name="Original",
        slug="custom-slug",
        description="Desc",
        tags=["a"],
        actor="author",
    )

    updated = await repository.update_workflow(
        created.id,
        name="Renamed",
        description="New desc",
        tags=["b"],
        is_archived=None,
        actor="editor",
    )
    assert updated.name == "Renamed"
    assert updated.description == "New desc"
    assert updated.tags == ["b"]
    assert updated.is_archived is False

    archived = await repository.archive_workflow(created.id, actor="editor")
    assert archived.is_archived is True

    unchanged = await repository.update_workflow(
        created.id,
        name=None,
        description=None,
        tags=["b"],
        is_archived=True,
        actor="editor",
    )
    assert unchanged.tags == ["b"]
    assert unchanged.is_archived is True
    # The most recent audit event should not include redundant metadata.
    assert unchanged.audit_log[-1].metadata == {}


@pytest.mark.asyncio()
async def test_update_missing_workflow(repository: WorkflowRepository) -> None:
    """Updating a missing workflow raises an explicit error."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.update_workflow(
            uuid4(),
            name=None,
            description=None,
            tags=None,
            is_archived=None,
            actor="tester",
        )


@pytest.mark.asyncio()
async def test_version_management(repository: WorkflowRepository) -> None:
    """Version CRUD supports numbering, listing, and retrieval."""

    workflow = await repository.create_workflow(
        name="Versioned",
        slug=None,
        description=None,
        tags=None,
        actor="author",
    )

    first = await repository.create_version(
        workflow.id,
        graph={"nodes": ["a"], "edges": []},
        metadata={"first": True},
        notes=None,
        created_by="author",
    )
    second = await repository.create_version(
        workflow.id,
        graph={"nodes": ["a", "b"], "edges": []},
        metadata={"first": False},
        notes="update",
        created_by="author",
    )

    versions = await repository.list_versions(workflow.id)
    assert [version.version for version in versions] == [1, 2]
    assert versions[0].id == first.id

    looked_up = await repository.get_version_by_number(workflow.id, 2)
    assert looked_up.id == second.id

    fetched = await repository.get_version(second.id)
    assert fetched.id == second.id

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_version_by_number(workflow.id, 3)

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_version_by_number(uuid4(), 1)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_version(uuid4())

    diff = await repository.diff_versions(workflow.id, 1, 2)
    assert isinstance(diff, VersionDiff)
    assert diff.base_version == 1
    assert diff.target_version == 2
    assert any('+    "b"' in line for line in diff.diff)


@pytest.mark.asyncio()
async def test_create_version_without_workflow(
    repository: WorkflowRepository,
) -> None:
    """Creating a version for an unknown workflow fails."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.create_version(
            uuid4(),
            graph={},
            metadata={},
            notes=None,
            created_by="actor",
        )


@pytest.mark.asyncio()
async def test_run_lifecycle(repository: WorkflowRepository) -> None:
    """Runs can transition through success, failure, and cancellation."""

    workflow = await repository.create_workflow(
        name="Runnable",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    # Successful run path
    run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="runner",
        input_payload={"payload": True},
    )
    started = await repository.mark_run_started(run.id, actor="runner")
    assert started.status == "running"
    succeeded = await repository.mark_run_succeeded(
        run.id, actor="runner", output={"result": "ok"}
    )
    assert succeeded.status == "succeeded"
    assert succeeded.output_payload == {"result": "ok"}

    # Failed run path
    failed_run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="runner",
        input_payload={},
    )
    failed = await repository.mark_run_failed(
        failed_run.id, actor="runner", error="boom"
    )
    assert failed.status == "failed"
    assert failed.error == "boom"

    # Cancelled run path
    cancelled_run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="runner",
        input_payload={},
    )
    cancelled = await repository.mark_run_cancelled(
        cancelled_run.id, actor="runner", reason="stop"
    )
    assert cancelled.status == "cancelled"
    assert cancelled.error == "stop"

    runs = await repository.list_runs_for_workflow(workflow.id)
    assert {run.status for run in runs} == {"succeeded", "failed", "cancelled"}


@pytest.mark.asyncio()
async def test_run_error_paths(repository: WorkflowRepository) -> None:
    """All run error branches raise the correct exceptions."""

    missing_workflow_id = uuid4()
    with pytest.raises(WorkflowNotFoundError):
        await repository.create_run(
            missing_workflow_id,
            workflow_version_id=uuid4(),
            triggered_by="actor",
            input_payload={},
        )

    workflow = await repository.create_workflow(
        name="Run Errors",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    _ = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.create_run(
            workflow.id,
            workflow_version_id=uuid4(),
            triggered_by="actor",
            input_payload={},
        )

    other_workflow = await repository.create_workflow(
        name="Other",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    mismatched_version = await repository.create_version(
        other_workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.create_run(
            workflow.id,
            workflow_version_id=mismatched_version.id,
            triggered_by="actor",
            input_payload={},
        )

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.get_run(uuid4())

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_started(uuid4(), actor="actor")

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_succeeded(uuid4(), actor="actor", output=None)

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_failed(uuid4(), actor="actor", error="err")

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.mark_run_cancelled(uuid4(), actor="actor", reason=None)


@pytest.mark.asyncio()
async def test_manual_dispatch_defaults_to_latest_version(
    repository: WorkflowRepository,
) -> None:
    """Manual dispatch without explicit version targets the latest one."""

    workflow = await repository.create_workflow(
        name="Manual Flow",
        slug=None,
        description=None,
        tags=None,
        actor="author",
    )
    _ = await repository.create_version(
        workflow.id,
        graph={"nodes": ["start"], "edges": []},
        metadata={},
        notes=None,
        created_by="author",
    )
    second_version = await repository.create_version(
        workflow.id,
        graph={"nodes": ["start", "end"], "edges": []},
        metadata={},
        notes=None,
        created_by="author",
    )

    request = ManualDispatchRequest(
        workflow_id=workflow.id,
        actor="operator",
        runs=[ManualDispatchItem(input_payload={"foo": "bar"})],
    )

    runs = await repository.dispatch_manual_runs(request)
    assert len(runs) == 1
    run = runs[0]
    assert run.triggered_by == "manual"
    assert run.workflow_version_id == second_version.id
    assert run.input_payload == {"foo": "bar"}

    stored = await repository.get_run(run.id)
    assert stored.audit_log[0].actor == "operator"


@pytest.mark.asyncio()
async def test_manual_dispatch_supports_batch_runs(
    repository: WorkflowRepository,
) -> None:
    """Batch dispatch respects explicit version overrides and ordering."""

    workflow = await repository.create_workflow(
        name="Batch Flow",
        slug=None,
        description=None,
        tags=None,
        actor="author",
    )
    first_version = await repository.create_version(
        workflow.id,
        graph={"nodes": ["start"], "edges": []},
        metadata={},
        notes=None,
        created_by="author",
    )
    second_version = await repository.create_version(
        workflow.id,
        graph={"nodes": ["start", "branch"], "edges": []},
        metadata={},
        notes=None,
        created_by="author",
    )

    request = ManualDispatchRequest(
        workflow_id=workflow.id,
        actor="batcher",
        runs=[
            ManualDispatchItem(
                workflow_version_id=first_version.id,
                input_payload={"step": 1},
            ),
            ManualDispatchItem(
                workflow_version_id=second_version.id,
                input_payload={"step": 2},
            ),
        ],
    )

    runs = await repository.dispatch_manual_runs(request)
    assert [run.triggered_by for run in runs] == ["manual_batch", "manual_batch"]
    assert [run.workflow_version_id for run in runs] == [
        first_version.id,
        second_version.id,
    ]
    assert [run.input_payload for run in runs] == [{"step": 1}, {"step": 2}]


@pytest.mark.asyncio()
async def test_manual_dispatch_rejects_unknown_versions(
    repository: WorkflowRepository,
) -> None:
    """Dispatch raises when referencing missing versions or workflows."""

    workflow = await repository.create_workflow(
        name="Error Flow",
        slug=None,
        description=None,
        tags=None,
        actor="author",
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.dispatch_manual_runs(
            ManualDispatchRequest(
                workflow_id=workflow.id,
                actor="operator",
                runs=[ManualDispatchItem(workflow_version_id=uuid4())],
            )
        )

    with pytest.raises(WorkflowNotFoundError):
        await repository.dispatch_manual_runs(
            ManualDispatchRequest(
                workflow_id=uuid4(),
                actor="operator",
                runs=[ManualDispatchItem()],
            )
        )

    other_workflow = await repository.create_workflow(
        name="Foreign Versions",
        slug=None,
        description=None,
        tags=None,
        actor="author",
    )
    foreign_version = await repository.create_version(
        other_workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="author",
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.dispatch_manual_runs(
            ManualDispatchRequest(
                workflow_id=workflow.id,
                actor="operator",
                runs=[
                    ManualDispatchItem(
                        workflow_version_id=foreign_version.id,
                    )
                ],
            )
        )


@pytest.mark.asyncio()
async def test_configure_retry_policy_and_schedule_decision(
    repository: WorkflowRepository,
) -> None:
    """Retry policy configuration surfaces scheduling decisions."""

    workflow = await repository.create_workflow(
        name="Retry Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    config = RetryPolicyConfig(
        max_attempts=2,
        initial_delay_seconds=10.0,
        jitter_factor=0.0,
    )
    stored = await repository.configure_retry_policy(workflow.id, config)
    assert stored.max_attempts == 2

    run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="webhook",
        input_payload={},
        actor="tester",
    )

    first = await repository.schedule_retry_for_run(
        run.id, failed_at=datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
    )
    assert first is not None
    assert first.retry_number == 1

    second = await repository.schedule_retry_for_run(
        run.id, failed_at=datetime(2025, 1, 1, 10, 10, tzinfo=UTC)
    )
    assert second is None


@pytest.mark.asyncio()
async def test_create_run_with_cron_source_tracks_overlap(
    repository: WorkflowRepository,
) -> None:
    """Cron-sourced runs register overlap tracking even without stored state."""

    workflow = await repository.create_workflow(
        name="Cron Indexed",
        slug=None,
        description=None,
        tags=None,
        actor="cron",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="cron",
    )

    run = await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="cron",
        input_payload={},
    )
    assert repository._trigger_layer._cron_run_index[run.id] == workflow.id

    await repository.mark_run_started(run.id, actor="cron")
    await repository.mark_run_succeeded(run.id, actor="cron", output=None)
    assert run.id not in repository._trigger_layer._cron_run_index


@pytest.mark.asyncio()
async def test_list_entities_error_paths(
    repository: WorkflowRepository,
) -> None:
    """Listing versions or runs for unknown workflows surfaces not found errors."""

    missing_id = uuid4()
    with pytest.raises(WorkflowNotFoundError):
        await repository.list_versions(missing_id)

    with pytest.raises(WorkflowNotFoundError):
        await repository.list_runs_for_workflow(missing_id)


@pytest.mark.asyncio()
async def test_retry_configuration_requires_existing_workflow(
    repository: WorkflowRepository,
) -> None:
    """Retry configuration helpers enforce workflow existence."""

    missing_id = uuid4()
    with pytest.raises(WorkflowNotFoundError):
        await repository.configure_retry_policy(missing_id, RetryPolicyConfig())

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_retry_policy_config(missing_id)


@pytest.mark.asyncio()
async def test_schedule_retry_for_run_requires_existing_run(
    repository: WorkflowRepository,
) -> None:
    """Retry scheduling for unknown runs raises the expected error."""

    with pytest.raises(WorkflowRunNotFoundError):
        await repository.schedule_retry_for_run(uuid4())


@pytest.mark.asyncio()
async def test_sqlite_repository_hydrates_failed_run_retry_state(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Failed runs maintain retry state after the SQLite repo restarts."""

    db_path = tmp_path_factory.mktemp("repo") / "workflow.sqlite"
    repository = SqliteWorkflowRepository(db_path)
    restart_repository: SqliteWorkflowRepository | None = None

    try:
        workflow = await repository.create_workflow(
            name="Retryable", slug=None, description=None, tags=None, actor="author"
        )
        await repository.create_version(
            workflow.id,
            graph={},
            metadata={},
            notes=None,
            created_by="author",
        )
        await repository.configure_retry_policy(
            workflow.id,
            RetryPolicyConfig(
                max_attempts=2, initial_delay_seconds=1.0, jitter_factor=0.0
            ),
        )
        await repository.configure_webhook_trigger(
            workflow.id,
            WebhookTriggerConfig(allowed_methods={"POST"}),
        )
        await repository.configure_cron_trigger(
            workflow.id,
            CronTriggerConfig(expression="0 9 * * *", timezone="UTC"),
        )

        (cron_run,) = await repository.dispatch_due_cron_runs(
            now=datetime(2025, 1, 1, 9, 0, tzinfo=UTC)
        )

        (run,) = await repository.dispatch_manual_runs(
            ManualDispatchRequest(
                workflow_id=workflow.id,
                actor="tester",
                runs=[ManualDispatchItem()],
            )
        )
        await repository.mark_run_failed(run.id, actor="worker", error="boom")

        restart_repository = SqliteWorkflowRepository(db_path)
        decision = await restart_repository.schedule_retry_for_run(run.id)
        assert decision is not None
        assert decision.retry_number == 1
        webhook_config = await restart_repository.get_webhook_trigger_config(
            workflow.id
        )
        assert "POST" in webhook_config.allowed_methods
        cron_config = await restart_repository.get_cron_trigger_config(workflow.id)
        assert cron_config.expression == "0 9 * * *"
        assert cron_run.id in restart_repository._trigger_layer._cron_run_index
    finally:
        if restart_repository is not None:
            await restart_repository.reset()
        await repository.reset()


@pytest.mark.asyncio()
async def test_sqlite_handle_webhook_trigger_success(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Webhook triggers enqueue runs with normalized payloads."""

    db_path = tmp_path_factory.mktemp("repo") / "webhook.sqlite"
    repository = SqliteWorkflowRepository(db_path)

    try:
        workflow = await repository.create_workflow(
            name="Webhook Flow",
            slug=None,
            description=None,
            tags=None,
            actor="author",
        )
        await repository.create_version(
            workflow.id,
            graph={},
            metadata={},
            notes=None,
            created_by="author",
        )
        await repository.configure_webhook_trigger(
            workflow.id, WebhookTriggerConfig(allowed_methods={"POST"})
        )

        run = await repository.handle_webhook_trigger(
            workflow.id,
            method="POST",
            headers={"X-Test": "value"},
            query_params={"ok": "1"},
            payload={"payload": True},
            source_ip="127.0.0.1",
        )

        assert run.triggered_by == "webhook"
        stored = await repository.get_run(run.id)
        assert stored.input_payload["body"] == {"payload": True}
        assert stored.input_payload["query_params"] == {"ok": "1"}
    finally:
        await repository.reset()


@pytest.mark.asyncio()
async def test_sqlite_manual_dispatch_rejects_foreign_versions(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Manual dispatch guards against versions from other workflows."""

    db_path = tmp_path_factory.mktemp("repo") / "manual.sqlite"
    repository = SqliteWorkflowRepository(db_path)

    try:
        workflow = await repository.create_workflow(
            name="Primary",
            slug=None,
            description=None,
            tags=None,
            actor="author",
        )
        await repository.create_version(
            workflow.id,
            graph={},
            metadata={},
            notes=None,
            created_by="author",
        )
        other_workflow = await repository.create_workflow(
            name="Foreign",
            slug=None,
            description=None,
            tags=None,
            actor="author",
        )
        other_version = await repository.create_version(
            other_workflow.id,
            graph={},
            metadata={},
            notes=None,
            created_by="author",
        )

        with pytest.raises(WorkflowVersionNotFoundError):
            await repository.dispatch_manual_runs(
                ManualDispatchRequest(
                    workflow_id=workflow.id,
                    actor="operator",
                    runs=[
                        ManualDispatchItem(
                            workflow_version_id=other_version.id,
                        )
                    ],
                )
            )
    finally:
        await repository.reset()


@pytest.mark.asyncio()
async def test_sqlite_ensure_initialized_concurrent_calls(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Concurrent initialization requests exit early once setup completes."""

    db_path = tmp_path_factory.mktemp("repo") / "init.sqlite"
    repository = SqliteWorkflowRepository(db_path)

    try:
        await asyncio.gather(
            repository._ensure_initialized(), repository._ensure_initialized()
        )
        assert repository._initialized is True
    finally:
        await repository.reset()


@pytest.mark.asyncio()
async def test_inmemory_latest_version_missing_instance() -> None:
    """Missing latest version objects surface a dedicated error."""

    repository = InMemoryWorkflowRepository()

    workflow = await repository.create_workflow(
        name="Latest", slug=None, description=None, tags=None, actor="tester"
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="tester",
    )

    repository._versions.pop(version.id)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_latest_version(workflow.id)


@pytest.mark.asyncio()
async def test_inmemory_handle_webhook_missing_version_object() -> None:
    """Webhook dispatch raises when the latest version is missing."""

    repository = InMemoryWorkflowRepository()

    workflow = await repository.create_workflow(
        name="Webhook", slug=None, description=None, tags=None, actor="tester"
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="tester",
    )
    await repository.configure_webhook_trigger(
        workflow.id, WebhookTriggerConfig(allowed_methods={"POST"})
    )

    repository._versions.pop(version.id)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.handle_webhook_trigger(
            workflow.id,
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )


@pytest.mark.asyncio()
async def test_inmemory_cron_dispatch_skips_missing_versions() -> None:
    """Cron dispatch ignores schedules when the latest version is missing."""

    repository = InMemoryWorkflowRepository()

    workflow = await repository.create_workflow(
        name="Cron", slug=None, description=None, tags=None, actor="owner"
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )
    await repository.configure_cron_trigger(
        workflow.id, CronTriggerConfig(expression="0 12 * * *", timezone="UTC")
    )

    repository._versions.pop(version.id)

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    )
    assert runs == []


@pytest.mark.asyncio()
async def test_retry_policy_round_trip(
    repository: WorkflowRepository,
) -> None:
    """Retry policy configuration can be stored and retrieved."""

    workflow = await repository.create_workflow(
        name="Retry Policy",
        slug=None,
        description=None,
        tags=None,
        actor="qa",
    )
    config = RetryPolicyConfig(max_attempts=4, initial_delay_seconds=12.5)

    stored = await repository.configure_retry_policy(workflow.id, config)
    assert stored.max_attempts == 4
    assert stored.initial_delay_seconds == 12.5

    fetched = await repository.get_retry_policy_config(workflow.id)
    assert fetched.max_attempts == 4
    assert fetched.initial_delay_seconds == 12.5


@pytest.mark.asyncio()
async def test_reset_clears_internal_state(
    repository: WorkflowRepository,
) -> None:
    """Reset removes all previously stored workflows, versions, and runs."""

    workflow = await repository.create_workflow(
        name="Reset",
        slug=None,
        description=None,
        tags=None,
        actor="actor",
    )
    version = await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="actor",
    )
    await repository.create_run(
        workflow.id,
        workflow_version_id=version.id,
        triggered_by="actor",
        input_payload={},
    )

    await repository.reset()

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_workflow(workflow.id)


def test_repository_error_hierarchy() -> None:
    """Ensure repository-specific errors inherit from the common base."""

    assert issubclass(WorkflowNotFoundError, RepositoryError)
    assert issubclass(WorkflowVersionNotFoundError, RepositoryError)
    assert issubclass(WorkflowRunNotFoundError, RepositoryError)


@pytest.mark.asyncio()
async def test_get_latest_version_validation(
    repository: WorkflowRepository,
) -> None:
    """Latest version retrieval enforces workflow and version existence."""

    workflow = await repository.create_workflow(
        name="Latest", slug=None, description=None, tags=None, actor="tester"
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_latest_version(workflow.id)

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_latest_version(uuid4())

    version = await repository.create_version(
        workflow.id,
        graph={"nodes": []},
        metadata={},
        notes=None,
        created_by="tester",
    )
    latest = await repository.get_latest_version(workflow.id)
    assert latest.id == version.id
    await _remove_version(repository, version.id)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.get_latest_version(workflow.id)


@pytest.mark.asyncio()
async def test_webhook_configuration_requires_workflow(
    repository: WorkflowRepository,
) -> None:
    """Configuring a webhook for a missing workflow raises an error."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.configure_webhook_trigger(uuid4(), WebhookTriggerConfig())


@pytest.mark.asyncio()
async def test_webhook_configuration_roundtrip(
    repository: WorkflowRepository,
) -> None:
    """Webhook configuration persists and returns deep copies."""

    workflow = await repository.create_workflow(
        name="Webhook", slug=None, description=None, tags=None, actor="tester"
    )
    config = WebhookTriggerConfig(allowed_methods={"POST", "GET"})

    stored = await repository.configure_webhook_trigger(workflow.id, config)
    assert set(stored.allowed_methods) == {"POST", "GET"}

    fetched = await repository.get_webhook_trigger_config(workflow.id)
    assert fetched == stored


@pytest.mark.asyncio()
async def test_handle_webhook_trigger_missing_resources(
    repository: WorkflowRepository,
) -> None:
    """Webhook handling raises when workflow or versions are missing."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.handle_webhook_trigger(
            uuid4(),
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )

    workflow = await repository.create_workflow(
        name="Webhook Flow", slug=None, description=None, tags=None, actor="tester"
    )

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.handle_webhook_trigger(
            workflow.id,
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )

    version = await repository.create_version(
        workflow.id,
        graph={"nodes": []},
        metadata={},
        notes=None,
        created_by="tester",
    )
    await repository.configure_webhook_trigger(workflow.id, WebhookTriggerConfig())

    await _remove_version(repository, version.id)

    with pytest.raises(WorkflowVersionNotFoundError):
        await repository.handle_webhook_trigger(
            workflow.id,
            method="POST",
            headers={},
            query_params={},
            payload={},
            source_ip=None,
        )


@pytest.mark.asyncio()
async def test_cron_trigger_configuration_and_dispatch(
    repository: WorkflowRepository,
) -> None:
    """Cron trigger configuration is persisted and schedules runs."""

    workflow = await repository.create_workflow(
        name="Cron Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    saved = await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 12 * * *", timezone="UTC"),
    )
    assert saved.expression == "0 12 * * *"

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    )
    assert len(runs) == 1
    run = runs[0]
    assert run.triggered_by == "cron"
    assert run.input_payload["scheduled_for"] == "2025-01-01T12:00:00+00:00"

    repeat = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 12, 0, tzinfo=UTC)
    )
    assert repeat == []

    fetched = await repository.get_cron_trigger_config(workflow.id)
    assert fetched.expression == "0 12 * * *"


@pytest.mark.asyncio()
async def test_cron_trigger_requires_existing_workflow(
    repository: WorkflowRepository,
) -> None:
    """Cron trigger helpers raise when the workflow is unknown."""

    with pytest.raises(WorkflowNotFoundError):
        await repository.configure_cron_trigger(uuid4(), CronTriggerConfig())

    with pytest.raises(WorkflowNotFoundError):
        await repository.get_cron_trigger_config(uuid4())


@pytest.mark.asyncio()
async def test_cron_trigger_overlap_guard(
    repository: WorkflowRepository,
) -> None:
    """Cron scheduler skips scheduling when an active run exists."""

    workflow = await repository.create_workflow(
        name="Overlap Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 9 * * *", timezone="UTC"),
    )

    first = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 9, 0, tzinfo=UTC)
    )
    assert len(first) == 1
    run_id = first[0].id

    skipped = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
    )
    assert skipped == []

    await repository.mark_run_started(run_id, actor="cron")
    await repository.mark_run_succeeded(run_id, actor="cron", output=None)

    next_runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 2, 9, 0, tzinfo=UTC)
    )
    assert len(next_runs) == 1


@pytest.mark.asyncio()
async def test_dispatch_due_cron_runs_handles_edge_cases(
    repository: WorkflowRepository,
) -> None:
    """Cron dispatcher gracefully skips invalid and incomplete state entries."""

    naive_now = datetime(2025, 1, 1, 11, 0)

    # Entry without a persisted workflow.
    repository._trigger_layer.configure_cron(uuid4(), CronTriggerConfig())

    # Workflow without versions.
    workflow_without_versions = await repository.create_workflow(
        name="No Versions",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    repository._trigger_layer.configure_cron(
        workflow_without_versions.id,
        CronTriggerConfig(expression="0 11 * * *", timezone="UTC"),
    )

    # Workflow with a missing latest version object.
    workflow_missing_version = await repository.create_workflow(
        name="Missing Version",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    orphaned_version = await repository.create_version(
        workflow_missing_version.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )
    await _remove_version(repository, orphaned_version.id)
    repository._trigger_layer.configure_cron(
        workflow_missing_version.id,
        CronTriggerConfig(expression="0 11 * * *", timezone="UTC"),
    )

    # Workflow that is not yet due.
    workflow_not_due = await repository.create_workflow(
        name="Not Due",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow_not_due.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )
    repository._trigger_layer.configure_cron(
        workflow_not_due.id,
        CronTriggerConfig(expression="0 12 * * *", timezone="UTC"),
    )

    runs = await repository.dispatch_due_cron_runs(now=naive_now)
    assert runs == []

    # Once the missing version is created the original occurrence is dispatched.
    await repository.create_version(
        workflow_without_versions.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    retried_runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 11, 0, tzinfo=UTC)
    )
    assert len(retried_runs) == 1
    assert retried_runs[0].triggered_by == "cron"


@pytest.mark.asyncio()
@pytest.mark.parametrize("backend", ["memory", "sqlite"])
async def test_cron_dispatch_skips_unhealthy_workflows(
    backend: str, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Cron dispatch continues processing plans when health checks fail."""

    service = StubCredentialService()
    if backend == "memory":
        repository: WorkflowRepository = InMemoryWorkflowRepository(service)
    else:
        db_path = tmp_path_factory.mktemp("repo-health") / "workflows.sqlite"
        repository = SqliteWorkflowRepository(db_path, credential_service=service)

    try:
        unhealthy = await repository.create_workflow(
            name="Unhealthy Cron",
            slug=None,
            description=None,
            tags=None,
            actor="owner",
        )
        healthy = await repository.create_workflow(
            name="Healthy Cron",
            slug=None,
            description=None,
            tags=None,
            actor="owner",
        )

        versions: dict[UUID, UUID] = {}
        for workflow in (unhealthy, healthy):
            version = await repository.create_version(
                workflow.id,
                graph={},
                metadata={},
                notes=None,
                created_by="owner",
            )
            versions[workflow.id] = version.id
            await repository.configure_cron_trigger(
                workflow.id,
                CronTriggerConfig(expression="0 9 * * *", timezone="UTC"),
            )

        service.mark_unhealthy(unhealthy.id)

        runs = await repository.dispatch_due_cron_runs(
            now=datetime(2025, 1, 1, 9, 0, tzinfo=UTC)
        )

        assert [unhealthy.id, healthy.id] == service.checked_workflows
        assert len(runs) == 1
        assert runs[0].workflow_version_id == versions[healthy.id]
    finally:
        await repository.reset()


@pytest.mark.asyncio()
async def test_dispatch_due_cron_runs_respects_overlap_without_creating_runs(
    repository: WorkflowRepository,
) -> None:
    """Cron dispatcher skips scheduling when overlap guard is active."""

    workflow = await repository.create_workflow(
        name="Guarded Cron",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 7 * * *", timezone="UTC"),
    )
    active_run_id = uuid4()
    repository._trigger_layer.track_run(workflow.id, active_run_id)
    repository._trigger_layer.register_cron_run(active_run_id)

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 7, 0, tzinfo=UTC)
    )
    assert runs == []


@pytest.mark.asyncio()
async def test_cron_trigger_timezone_alignment(
    repository: WorkflowRepository,
) -> None:
    """Cron scheduler respects configured timezones when dispatching."""

    workflow = await repository.create_workflow(
        name="TZ Flow",
        slug=None,
        description=None,
        tags=None,
        actor="owner",
    )
    await repository.create_version(
        workflow.id,
        graph={},
        metadata={},
        notes=None,
        created_by="owner",
    )

    await repository.configure_cron_trigger(
        workflow.id,
        CronTriggerConfig(expression="0 9 * * *", timezone="America/Los_Angeles"),
    )

    runs = await repository.dispatch_due_cron_runs(
        now=datetime(2025, 1, 1, 17, 0, tzinfo=UTC)
    )
    assert len(runs) == 1
