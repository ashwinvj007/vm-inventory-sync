import json
from pathlib import Path
from models import VM
from collectors.base import Collector

FILE = Path(__file__).parent.parent / "fixtures" / "vmware.json"

class VmwareCollector(Collector):
    name = "vmware"

    def collect(self) -> list[VM]:
        vms = []
        for r in json.loads(FILE.read_text()):
            vms.append(VM(
                source="vmware",
                external_id=r["moid"],
                hostname=r["name"],
                ips=[r["ip"]],
                os=r["guest_os"],
                cpu=r["num_cpu"],
                ram_mb=r["memory_mb"],
                disk_gb=r["disk_gb"],
                tags={},
                owner=r.get("owner", ""),
                power_state="on" if r["power_state"] == "poweredOn" else "off",
                location=r["cluster"],
            ))
        return vms