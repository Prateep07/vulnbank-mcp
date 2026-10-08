import os
import re
from typing import Optional

import httpx
from pydantic import BaseModel, Field

from nitrostack import ExecutionContext, injectable, tool, widget

VULNBANK_BASE_URL = (
    os.getenv("VULNBANK_BASE_URL") or "http://127.0.0.1:5000"
).rstrip("/")


class EmptyInput(BaseModel):
    pass


class LoginInput(BaseModel):
    username: str = Field(
        description="VulnBank username for the authorized training account."
    )
    password: str = Field(
        description="Password for the authorized training account."
    )


class AccountInput(BaseModel):
    account_id: int = Field(
        description="VulnBank account ID to retrieve."
    )


class TransferInput(BaseModel):
    to_account: int = Field(
        description="Destination VulnBank account ID."
    )
    amount: float = Field(
        gt=0,
        description="Amount to transfer."
    )


class RestoreInput(BaseModel):
    data: str = Field(
        description="Serialized training data accepted by the VulnBank restore endpoint."
    )


class ImportInput(BaseModel):
    url: str = Field(
        description="URL to request through the VulnBank import functionality."
    )


VULNERABILITIES = [
    {
        "id": "A01",
        "name": "Broken Access Control",
        "endpoint": "/account/<account_id>",
        "severity": "High",
        "description": "Account ownership is not properly enforced.",
    },
    {
        "id": "A02",
        "name": "Cryptographic Failures",
        "endpoint": "/login",
        "severity": "High",
        "description": "The training application uses weak password hashing.",
    },
    {
        "id": "A03",
        "name": "Injection",
        "endpoint": "/login",
        "severity": "Critical",
        "description": "The login endpoint intentionally demonstrates SQL injection.",
    },
    {
        "id": "A04",
        "name": "Insecure Design",
        "endpoint": "/transfer",
        "severity": "High",
        "description": "The transfer workflow intentionally lacks important security controls.",
    },
    {
        "id": "A05",
        "name": "Security Misconfiguration",
        "endpoint": "/admin",
        "severity": "High",
        "description": "The training admin endpoint lacks proper authorization.",
    },
    {
        "id": "A08",
        "name": "Software and Data Integrity Failures",
        "endpoint": "/restore",
        "severity": "Critical",
        "description": "The training restore endpoint demonstrates unsafe deserialization.",
    },
    {
        "id": "A10",
        "name": "SSRF",
        "endpoint": "/import",
        "severity": "High",
        "description": "The training import endpoint accepts a user-controlled URL.",
    },
]


def response_data(
    response: httpx.Response,
    body_limit: int = 5000,
) -> dict:
    content_type = response.headers.get("content-type", "")

    result = {
        "status_code": response.status_code,
        "url": str(response.url),
        "content_type": content_type,
        "ok": response.is_success,
    }

    if "text/html" in content_type.lower():
        title_match = re.search(
            r"<title[^>]*>(.*?)</title>",
            response.text,
            re.IGNORECASE | re.DOTALL,
        )

        title = None
        if title_match:
            title = " ".join(title_match.group(1).split())

        text = re.sub(
            r"<[^>]+>",
            " ",
            response.text,
        )

        text = " ".join(text.split())

        result["title"] = title
        result["text"] = text[:1200]
    else:
        result["body"] = response.text[:body_limit]

    return result


@injectable(deps=[])
class VulnBankTools:

    @tool(
        name="show_vulnbank_status",
        description="Check whether the VulnBank backend is reachable and display its configured endpoints.",
        input_schema=EmptyInput,
    )
    @widget("vulnbank")
    async def show_vulnbank_status(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:
        endpoints = [
            "/login",
            "/logout",
            "/dashboard",
            "/account/<account_id>",
            "/transfer",
            "/admin",
            "/restore",
            "/import",
        ]

        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.get("/login")

                return {
                    "name": "VulnBank",
                    "status": "connected",
                    "base_url": VULNBANK_BASE_URL,
                    "http_status": response.status_code,
                    "backend_reachable": True,
                    "endpoints": endpoints,
                }

        except Exception as error:
            return {
                "name": "VulnBank",
                "status": "unreachable",
                "base_url": VULNBANK_BASE_URL,
                "http_status": None,
                "backend_reachable": False,
                "error": str(error),
                "endpoints": endpoints,
            }

    @tool(
        name="list_vulnerabilities",
        description="List the intentionally vulnerable security labs exposed by VulnBank.",
        input_schema=EmptyInput,
    )
    @widget("vulnbank")
    async def list_vulnerabilities(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:
        severity_counts = {}

        for vulnerability in VULNERABILITIES:
            severity = vulnerability["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "application": "VulnBank",
            "base_url": VULNBANK_BASE_URL,
            "total": len(VULNERABILITIES),
            "severity_counts": severity_counts,
            "vulnerabilities": VULNERABILITIES,
        }

    @tool(
        name="login",
        description="Authenticate to the VulnBank training application using an authorized test account.",
        input_schema=LoginInput,
    )
    async def login(
        self,
        input: LoginInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    "/login",
                    data={
                        "username": input.username,
                        "password": input.password,
                    },
                )

                logged_in = "login" not in response.url.path.lower()

                return {
                    "status_code": response.status_code,
                    "logged_in": logged_in,
                    "username": input.username,
                    "session_stored": True,
                    "response": response_data(response),
                }

        except Exception as error:
            return {
                "status_code": None,
                "logged_in": False,
                "username": input.username,
                "session_stored": False,
                "error": str(error),
            }

    @tool(
        name="get_dashboard",
        description="Retrieve the authenticated VulnBank dashboard.",
        input_schema=EmptyInput,
    )
    async def get_dashboard(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.get("/dashboard")

                authenticated = (
                    response.status_code == 200
                    and "login" not in response.url.path.lower()
                )

                return {
                    "authenticated": authenticated,
                    "status_code": response.status_code,
                    "response": response_data(response),
                }

        except Exception as error:
            return {
                "authenticated": False,
                "status_code": None,
                "error": str(error),
            }

    @tool(
        name="get_account",
        description="Retrieve information for a VulnBank account.",
        input_schema=AccountInput,
    )
    async def get_account(
        self,
        input: AccountInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(f"/account/{input.account_id}")

                result = response_data(response)
                result["account_id"] = input.account_id

                return result

        except Exception as error:
            return {
                "account_id": input.account_id,
                "status_code": None,
                "ok": False,
                "error": str(error),
            }

    @tool(
        name="transfer",
        description="Perform a transfer in the VulnBank training application.",
        input_schema=TransferInput,
    )
    async def transfer(
        self,
        input: TransferInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    "/transfer",
                    data={
                        "to_account": input.to_account,
                        "amount": input.amount,
                    },
                )

                result = response_data(response)
                result["amount"] = input.amount
                result["to_account"] = input.to_account

                return result

        except Exception as error:
            return {
                "status_code": None,
                "ok": False,
                "amount": input.amount,
                "to_account": input.to_account,
                "error": str(error),
            }

    @tool(
        name="get_admin",
        description="Retrieve the VulnBank training application's administrative page.",
        input_schema=EmptyInput,
    )
    async def get_admin(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.get("/admin")

                return response_data(response)

        except Exception as error:
            return {
                "status_code": None,
                "ok": False,
                "error": str(error),
            }

    @tool(
        name="restore",
        description="Send authorized training data to the VulnBank restore endpoint.",
        input_schema=RestoreInput,
    )
    async def restore(
        self,
        input: RestoreInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    "/restore",
                    data={
                        "data": input.data,
                    },
                )

                return response_data(response)

        except Exception as error:
            return {
                "status_code": None,
                "ok": False,
                "error": str(error),
            }

    @tool(
        name="import_data",
        description="Request a URL through the VulnBank training application's import functionality.",
        input_schema=ImportInput,
    )
    async def import_data(
        self,
        input: ImportInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.post(
                    "/import",
                    data={
                        "url": input.url,
                    },
                )

                result = response_data(response)
                result["requested_url"] = input.url

                return result

        except Exception as error:
            return {
                "status_code": None,
                "ok": False,
                "requested_url": input.url,
                "error": str(error),
            }

    @tool(
        name="logout",
        description="Log out from the VulnBank training application.",
        input_schema=EmptyInput,
    )
    async def logout(
        self,
        input: EmptyInput,
        context: ExecutionContext,
    ) -> dict:
        try:
            async with httpx.AsyncClient(
                base_url=VULNBANK_BASE_URL,
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.get("/logout")

                return {
                    "status_code": response.status_code,
                    "logged_out": response.is_success,
                    "response": response_data(response),
                }

        except Exception as error:
            return {
                "status_code": None,
                "logged_out": False,
                "error": str(error),
            }