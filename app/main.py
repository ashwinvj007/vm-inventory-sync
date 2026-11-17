import sys
from dotenv import load_dotenv

load_dotenv()

from collectors.aws import AwsCollector
from collectors.azure import AzureCollector
from collectors.vmware import VmwareCollector
from netbox_client import NetBox
import sync


def collect_all():
    vms, ok = [], set()
    for c in (AwsCollector, AzureCollector, VmwareCollector):
        try:
            vms += c().collect()
            ok.add(c.name)
        except Exception as e:
            print(f"[warn] {c.name} collector failed, its VMs are left untouched: {e}")
    return vms, ok


def show(res, dry):
    tag = "DRY-RUN " if dry else ""
    print(f"{tag}created={len(res['created'])} updated={len(res['updated'])} "
          f"unchanged={res['unchanged']} decommissioned={len(res['decommissioned'])} "
          f"already_decommissioned={res['already_decommissioned']}")
    for n in res["created"]:
        print("  + new:", n)
    for n, d in res["updated"]:
        print("  ~ drift:", n)
        for k, (a, b) in d.items():
            print(f"      {k}: {a!r} -> {b!r}")
    for n in res["decommissioned"]:
        print("  - orphan:", n)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sync"
    if cmd not in ("sync", "report"):
        sys.exit("usage: python main.py [sync|report]")
    dry = cmd == "report"
    vms, ok = collect_all()
    show(sync.run(NetBox(), vms, ok, dry_run=dry), dry)