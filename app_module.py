from nitrostack import ConfigModule, module

from health.system_health import SystemHealthCheck
from modules.vulnbank.vulnbank_module import VulnBankModule


@module(
    name="app",
    imports=[
        ConfigModule.for_root(
            env_file_path=".env",
            defaults={"PORT": "3000"},
        ),
        VulnBankModule,
    ],
    providers=[SystemHealthCheck],
)
class AppModule:
    pass