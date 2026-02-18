"""Base Unit of Work pattern for Phoenix services."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


class BaseUnitOfWork:
    """Base class implementing the Unit of Work pattern for async SQLAlchemy.

    Subclass this in each service and add service-specific repository properties
    plus override ``_clear_repos()`` to clear cached repository instances on exit.

    Usage::

        class MyUnitOfWork(BaseUnitOfWork):
            def __init__(self, session=None, session_factory=None):
                super().__init__(session)
                self._session_factory = session_factory
                self._users = None

            @property
            def users(self) -> UserRepository:
                if self._users is None:
                    self._users = UserRepository(self.session)
                return self._users

            def _clear_repos(self):
                self._users = None

            def _create_session(self) -> AsyncSession:
                return self._session_factory()

        async with MyUnitOfWork() as uow:
            user = await uow.users.get(user_id)
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        # A session provided at construction time (e.g. from tests)
        self._injected_session = session
        # The active session used by this UoW
        self._session: Optional[AsyncSession] = None
        # Whether this UoW created the session (and must close it)
        self._owns_session = False

    @property
    def session(self) -> AsyncSession:
        """Return the active ``AsyncSession``, creating one lazily if needed."""
        if self._session is not None:
            return self._session

        if self._injected_session is not None:
            self._session = self._injected_session
            self._owns_session = False
            return self._session

        # Subclass must provide a session via _create_session()
        self._session = self._create_session()
        self._owns_session = True
        return self._session

    def _create_session(self) -> AsyncSession:
        """Create a new ``AsyncSession``.

        Override in subclasses to use a service-specific session factory.
        Raises ``NotImplementedError`` if not overridden and no session was injected.
        """
        raise NotImplementedError(
            "Either inject a session at construction time or override _create_session() "
            "in your UnitOfWork subclass."
        )

    def _clear_repos(self) -> None:
        """Clear cached repository instances.

        Override in subclasses to reset all ``_repo_*`` private attributes so
        they are re-created on next access after the context manager exits.
        """

    async def commit(self) -> None:
        """Explicitly commit the active transaction."""
        if self._session is not None:
            await self._session.commit()

    async def rollback(self) -> None:
        """Explicitly roll back the active transaction."""
        if self._session is not None:
            await self._session.rollback()

    async def __aenter__(self) -> "BaseUnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._owns_session and self._session is not None:
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()
            await self._session.close()
        elif self._session is not None:
            # External session: commit/rollback but do not close
            if exc_type:
                await self._session.rollback()
            else:
                await self._session.commit()

        self._clear_repos()

        if self._owns_session:
            self._session = None
            self._owns_session = False
