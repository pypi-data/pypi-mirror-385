import datetime


class TimestampMixin:
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None

    def pre_create(self) -> None:
        self.created_at = datetime.datetime.now(tz=datetime.UTC)
        super().pre_create()  # type: ignore[misc]

    async def apre_create(self) -> None:
        self.created_at = datetime.datetime.now(tz=datetime.UTC)
        await super().apre_create()  # type: ignore[misc]

    def pre_update(self) -> None:
        self.updated_at = datetime.datetime.now(tz=datetime.UTC)

        if not self.created_at:
            _metadata = self.get_metadata()  # type: ignore[attr-defined]
            self.created_at = datetime.datetime.fromtimestamp(_metadata.created_at / 1000, tz=datetime.UTC)

        super().pre_update()  # type: ignore[misc]

    async def apre_update(self) -> None:
        self.updated_at = datetime.datetime.now(tz=datetime.UTC)
        if not self.created_at:
            _metadata = await self.aget_metadata()  # type: ignore[attr-defined]
            self.created_at = datetime.datetime.fromtimestamp(_metadata.created_at / 1000, tz=datetime.UTC)

        await super().apre_update()  # type: ignore[misc]
