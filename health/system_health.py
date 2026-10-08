from nitrostack import health_check


@health_check(name="system")
class SystemHealthCheck:
    async def check(self) -> dict:
        return {
            "status": "ok",
            "service": "vulnbank-nitrostack",
        }