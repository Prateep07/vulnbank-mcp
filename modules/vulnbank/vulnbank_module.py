from nitrostack import module

from modules.vulnbank.vulnbank_resources_prompts import VulnBankResourcesPrompts
from modules.vulnbank.vulnbank_tools import VulnBankTools


@module(
    name="vulnbank",
    controllers=[
        VulnBankTools,
        VulnBankResourcesPrompts,
    ],
)
class VulnBankModule:
    pass