from nitrostack import module

from modules.vulnbank.vulnbank_tools import VulnBankTools
from modules.vulnbank.vulnbank_resources_prompts import VulnBankResourcesPrompts


@module(
    name="vulnbank",
    controllers=[
        VulnBankTools,
        VulnBankResourcesPrompts,
    ],
    providers=[],
    exports=[]
)
class VulnBankModule:
    pass