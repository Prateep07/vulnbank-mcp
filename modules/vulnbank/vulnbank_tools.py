import os
import httpx

from pydantic import BaseModel, Field
from nitrostack import injectable, tool, widget, ExecutionContext


VULNBANK_BASE_URL = os.getenv(
    "VULNBANK_BASE_URL",
    "http://127.0.0.1:5000"
).rstrip("/")


class EmptyInput(BaseModel):
    pass


class LoginInput(BaseModel):
    username: str = Field(description="VulnBank username")
    password: str = Field(description="VulnBank password")


class AccountInput(BaseModel):
    account_id: int = Field(description="VulnBank account ID")


class TransferInput(BaseModel):
    to_account: int = Field(description="Destination VulnBank account ID")
    amount: float = Field(description="Amount to transfer")


class RestoreInput(BaseModel):
    data: str = Field(description="Base64 encoded restore data")


class ImportInput(BaseModel):
    url: str = Field(description="URL to import")


@injectable(deps=[])
class VulnBankTools:

    def __init__(self):
        self.session_cookie = None

    def _cookies(self):
        if not self.session_cookie:
            return {}

        return {
            "session": self.session_cookie
        }

    @tool(
        "login",
        "Log in to VulnBank and store the session automatically.",
        LoginInput
    )
    async def login(
        self,
        input: LoginInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
        ) as client:

            response = await client.post(
                "/login",
                data={
                    "username": input.username,
                    "password": input.password,
                },
            )

            self.session_cookie = client.cookies.get("session")

            logged_in = response.url.path != "/login"

            return {
                "status_code": response.status_code,
                "logged_in": logged_in,
                "url": str(response.url),
                "body": response.text[:1000],
            }

    @tool(
        "get_dashboard",
        "Retrieve the logged-in user's VulnBank dashboard.",
        EmptyInput
    )
    async def get_dashboard(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.get("/dashboard")

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "body": response.text[:5000],
            }

    @tool(
        "get_account",
        "Retrieve a VulnBank account by account ID.",
        AccountInput
    )
    async def get_account(
        self,
        input: AccountInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.get(
                f"/account/{input.account_id}"
            )

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "body": response.text[:5000],
            }

    @tool(
        "transfer",
        "Transfer money from the logged-in user's account to another VulnBank account.",
        TransferInput
    )
    async def transfer(
        self,
        input: TransferInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.post(
                "/transfer",
                data={
                    "amount": input.amount,
                    "to_account": input.to_account,
                },
            )

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "body": response.text[:5000],
            }

    @tool(
        "get_admin",
        "Retrieve the VulnBank admin page.",
        EmptyInput
    )
    async def get_admin(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.get("/admin")

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "body": response.text[:5000],
            }

    @tool(
        "restore",
        "Send restore data to the VulnBank restore endpoint.",
        RestoreInput
    )
    async def restore(
        self,
        input: RestoreInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.get(
                "/restore",
                params={
                    "data": input.data
                },
            )

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "body": response.text[:5000],
            }

    @tool(
        "import_data",
        "Send a URL to the VulnBank import endpoint.",
        ImportInput
    )
    async def import_data(
        self,
        input: ImportInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.post(
                "/import",
                data={
                    "url": input.url
                },
            )

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "body": response.text[:5000],
            }

    @tool(
        "logout",
        "Log out of the current VulnBank session.",
        EmptyInput
    )
    async def logout(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:

        async with httpx.AsyncClient(
            base_url=VULNBANK_BASE_URL,
            follow_redirects=True,
            timeout=10.0,
            cookies=self._cookies(),
        ) as client:

            response = await client.get("/logout")

            self.session_cookie = None

            return {
                "status_code": response.status_code,
                "url": str(response.url),
                "logged_out": response.url.path == "/login",
            }

    @tool(
        "show_vulnbank_status",
        "Display the VulnBank application status and available endpoints.",
        EmptyInput
    )
    @widget("vulnbank-status")
    async def show_vulnbank_status(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:

        return {
            "name": "VulnBank",
            "status": "connected",
            "base_url": VULNBANK_BASE_URL,
            "endpoints": [
                "/login",
                "/dashboard",
                "/account/<account_id>",
                "/transfer",
                "/admin",
                "/restore",
                "/import",
            ],
        }