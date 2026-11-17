CF_FIELDS = ["source", "external_id", "owner", "ips", "os_name"]
STATUS = {"on": "active", "off": "offline"}


def cluster_name(vm):
    return f"{vm.source}-{vm.location}"


def flat(vm):
    return {
        "name": vm.hostname,
        "status": STATUS.get(vm.power_state, "offline"),
        "cluster": cluster_name(vm),
        "vcpus": float(vm.cpu),
        "memory": vm.ram_mb,
        "disk": vm.disk_gb * 1024,
        "cf.source": vm.source,
        "cf.external_id": vm.external_id,
        "cf.owner": vm.owner or "",
        "cf.ips": ", ".join(vm.ips),
        "cf.os_name": vm.os or "",
    }


def current(n):
    cf = n.get("custom_fields") or {}
    out = {
        "name": n["name"],
        "status": n["status"]["value"],
        "cluster": n["cluster"]["name"] if n.get("cluster") else None,
        "vcpus": float(n.get("vcpus") or 0),
        "memory": n.get("memory") or 0,
        "disk": n.get("disk") or 0,
    }
    for k in CF_FIELDS:
        out[f"cf.{k}"] = cf.get(k) or ""
    return out


def payload(f, clusters):
    p = {k: v for k, v in f.items() if not k.startswith("cf.")}
    p["cluster"] = clusters[f["cluster"]]
    p["custom_fields"] = {k[3:]: v for k, v in f.items() if k.startswith("cf.")}
    return p


def ensure_schema(nb, cluster_names, create=True):
    have = {f["name"] for f in nb.get_all("extras/custom-fields/")}
    ctype = None
    if create:
        for name in CF_FIELDS:
            if name not in have:
                nb._req("POST", "extras/custom-fields/", json={
                    "object_types": ["virtualization.virtualmachine"],
                    "type": "text",
                    "name": name,
                    "label": name.replace("_", " ").title(),
                    "required": False,
                })
        types = nb.get_all("virtualization/cluster-types/", {"slug": "mixed"})
        ctype = types[0]["id"] if types else nb._req(
            "POST", "virtualization/cluster-types/", json={"name": "Mixed", "slug": "mixed"})["id"]
    clusters = {c["name"]: c["id"] for c in nb.get_all("virtualization/clusters/")}
    if create:
        for n in sorted(set(cluster_names) - set(clusters)):
            clusters[n] = nb._req("POST", "virtualization/clusters/", json={"name": n, "type": ctype})["id"]
    return clusters


def run(nb, vms, sources, dry_run=False):
    clusters = ensure_schema(nb, {cluster_name(v) for v in vms}, create=not dry_run)
    index = {}
    for n in nb.get_all("virtualization/virtual-machines/"):
        cf = n.get("custom_fields") or {}
        if cf.get("source"):
            index[(cf["source"], cf.get("external_id"))] = n

    res = {"created": [], "updated": [], "unchanged": 0, "decommissioned": [], "already_decommissioned": 0}
    seen = set()

    for vm in vms:
        key = (vm.source, vm.external_id)
        seen.add(key)
        want = flat(vm)
        n = index.get(key)
        if n is None:
            res["created"].append(vm.hostname)
            if not dry_run:
                nb._req("POST", "virtualization/virtual-machines/", json=payload(want, clusters))
            continue
        cur = current(n)
        diff = {k: (cur.get(k), want[k]) for k in want if cur.get(k) != want[k]}
        if diff:
            res["updated"].append((vm.hostname, diff))
            if not dry_run:
                nb._req("PATCH", f"virtualization/virtual-machines/{n['id']}/", json=payload(want, clusters))
        else:
            res["unchanged"] += 1

    for key, n in index.items():
        if key[0] in sources and key not in seen:
            if n["status"]["value"] == "decommissioning":
                res["already_decommissioned"] += 1
            else:
                res["decommissioned"].append(n["name"])
                if not dry_run:
                    nb._req("PATCH", f"virtualization/virtual-machines/{n['id']}/",
                            json={"status": "decommissioning"})
    return res
