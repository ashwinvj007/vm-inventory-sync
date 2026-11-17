import json
from pathlib import Path
from models import VM
from collectors.base import Collector

FILE = Path(__file__).parent.parent / "fixtures" / "azure.json"
SIZES = {"Standard_B1s": (1, 1024), "Standard_B2s": (2, 4096), "Standard_D2s_v3": (2, 8192)}

class AzureCollector(Collector):
    name = "azure"

    def collect(self) -> list[VM]:
        vms = []
        for r in json.loads(FILE.read_text()):
            cpu, ram = SIZES.get(r["vmSize"], (1, 1024))
            vms.append(VM(
                source="azure",
                external_id=r["id"],
                hostname=r["name"],
                ips=[r["privateIp"]],
                os=r["osType"],
                cpu=cpu,
                ram_mb=ram,
                disk_gb=r["diskGb"],
                tags=r.get("tags", {}),
                owner=r.get("tags", {}).get("owner", ""),
                power_state="on" if r["powerState"] == "running" else "off",
                location=r["location"],
            ))
        return vms