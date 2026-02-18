"""Tests for phoenix_lib.db.unit_of_work.BaseUnitOfWork."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from phoenix_lib.db.unit_of_work import BaseUnitOfWork


def _make_mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


class ConcreteUoW(BaseUnitOfWork):
    """Minimal concrete UoW for testing."""

    def __init__(self, session=None, factory=None):
        super().__init__(session)
        self._factory = factory
        self._cleared = False

    def _create_session(self):
        if self._factory:
            return self._factory()
        raise NotImplementedError

    def _clear_repos(self):
        self._cleared = True


class TestBaseUnitOfWorkInit:
    def test_injected_session_stored(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        assert uow._injected_session is mock_session

    def test_no_session_none_initially(self):
        uow = ConcreteUoW()
        assert uow._session is None
        assert uow._owns_session is False


class TestSessionProperty:
    def test_uses_injected_session(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        assert uow.session is mock_session
        assert uow._owns_session is False

    def test_creates_session_via_factory(self):
        created = _make_mock_session()
        factory = MagicMock(return_value=created)
        uow = ConcreteUoW(factory=factory)
        assert uow.session is created
        assert uow._owns_session is True
        factory.assert_called_once()

    def test_session_cached_after_first_access(self):
        created = _make_mock_session()
        factory = MagicMock(return_value=created)
        uow = ConcreteUoW(factory=factory)
        _ = uow.session
        _ = uow.session
        factory.assert_called_once()

    def test_no_factory_raises(self):
        uow = BaseUnitOfWork()
        with pytest.raises(NotImplementedError):
            _ = uow.session


class TestCommitRollback:
    @pytest.mark.asyncio
    async def test_commit_calls_session_commit(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        _ = uow.session  # Trigger session init
        await uow.commit()
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rollback_calls_session_rollback(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        _ = uow.session
        await uow.rollback()
        mock_session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_commit_without_session_noop(self):
        uow = ConcreteUoW()
        # Should not raise even when no session exists
        await uow.commit()

    @pytest.mark.asyncio
    async def test_rollback_without_session_noop(self):
        uow = ConcreteUoW()
        await uow.rollback()


class TestContextManager:
    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        result = await uow.__aenter__()
        assert result is uow

    @pytest.mark.asyncio
    async def test_successful_exit_commits_injected_session(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        async with uow:
            _ = uow.session
        mock_session.commit.assert_awaited_once()
        # Injected session should NOT be closed
        mock_session.close.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_exception_exit_rolls_back_injected_session(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        with pytest.raises(ValueError):
            async with uow:
                _ = uow.session
                raise ValueError("test error")
        mock_session.rollback.assert_awaited_once()
        mock_session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_owned_session_closed_on_exit(self):
        created = _make_mock_session()
        factory = MagicMock(return_value=created)
        uow = ConcreteUoW(factory=factory)
        async with uow:
            _ = uow.session
        created.commit.assert_awaited_once()
        created.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_owned_session_rolled_back_and_closed_on_exception(self):
        created = _make_mock_session()
        factory = MagicMock(return_value=created)
        uow = ConcreteUoW(factory=factory)
        with pytest.raises(RuntimeError):
            async with uow:
                _ = uow.session
                raise RuntimeError("oops")
        created.rollback.assert_awaited_once()
        created.close.assert_awaited_once()
        created.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_clear_repos_called_on_exit(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        async with uow:
            _ = uow.session
        assert uow._cleared is True

    @pytest.mark.asyncio
    async def test_session_reset_after_exit(self):
        created = _make_mock_session()
        factory = MagicMock(return_value=created)
        uow = ConcreteUoW(factory=factory)
        async with uow:
            _ = uow.session
        assert uow._session is None
        assert uow._owns_session is False

    @pytest.mark.asyncio
    async def test_async_with_pattern(self):
        mock_session = _make_mock_session()
        uow = ConcreteUoW(session=mock_session)
        async with uow as ctx:
            assert ctx is uow
