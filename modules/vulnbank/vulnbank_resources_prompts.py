import os

from nitrostack import injectable, resource, prompt, ExecutionContext


VULNBANK_BASE_URL = (
    os.getenv("VULNBANK_BASE_URL")
    or "http://127.0.0.1:5000"
).rstrip("/")


@injectable(deps=[])
class VulnBankResourcesPrompts:

    @resource(
        uri="vulnbank://info",
        name="VulnBank Information",
        description="Information about the VulnBank training application.",
        mime_type="application/json",
    )
    async def vulnbank_info(
        self,
        context: ExecutionContext,
    ) -> dict:

        return {
            "name": "VulnBank",
            "description": (
                "Intentionally vulnerable Flask banking "
                "application for security training."
            ),
            "base_url": VULNBANK_BASE_URL,
            "routes": [
                "/login",
                "/logout",
                "/dashboard",
                "/account/<account_id>",
                "/transfer",
                "/admin",
                "/restore",
                "/import",
            ],
        }

    @resource(
        uri="vulnbank://security-labs",
        name="VulnBank Security Labs",
        description="Security vulnerabilities intentionally demonstrated by VulnBank.",
        mime_type="application/json",
    )
    async def security_labs(
        self,
        context: ExecutionContext,
    ) -> dict:

        return {
            "labs": [
                {
                    "id": "A01",
                    "name": "Broken Access Control",
                    "endpoint": "/account/<account_id>",
                },
                {
                    "id": "A02",
                    "name": "Cryptographic Failures",
                    "endpoint": "/login",
                },
                {
                    "id": "A03",
                    "name": "Injection",
                    "endpoint": "/login",
                },
                {
                    "id": "A04",
                    "name": "Insecure Design",
                    "endpoint": "/transfer",
                },
                {
                    "id": "A05",
                    "name": "Security Misconfiguration",
                    "endpoint": "/admin",
                },
                {
                    "id": "A08",
                    "name": "Software and Data Integrity Failures",
                    "endpoint": "/restore",
                },
                {
                    "id": "A10",
                    "name": "SSRF",
                    "endpoint": "/import",
                },
            ]
        }

    @prompt(
        name="vulnbank_security_audit",
        description="Generate a structured security audit workflow for VulnBank.",
        arguments=[],
    )
    async def vulnbank_security_audit(
        self,
        args: dict,
        context: ExecutionContext,
    ):

        return {
            "role": "user",
            "content": (
                "Perform a security assessment of the VulnBank "
                "training application. Review its authentication, "
                "authorization, account access, transfer logic, "
                "administrative access, deserialization functionality, "
                "and URL import functionality. For each finding, "
                "provide the endpoint, vulnerability category, impact, "
                "evidence to collect, and recommended remediation. "
                "Do not perform destructive actions or modify financial data."
            ),
        }

    @prompt(
        name="vulnbank_test_login",
        description="Create a safe workflow for testing VulnBank authentication.",
        arguments=[],
    )
    async def vulnbank_test_login(
        self,
        args: dict,
        context: ExecutionContext,
    ):

        return {
            "role": "user",
            "content": (
                "Test the VulnBank authentication flow using an "
                "authorized test account. Verify successful login, "
                "unsuccessful login, session creation, dashboard "
                "access, and logout. Do not use credentials belonging "
                "to real users."
            ),
        }