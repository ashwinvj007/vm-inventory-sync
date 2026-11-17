from dataclasses import dataclass, field

@dataclass
class VM:
    source: str
    external_id: str
    hostname: str
    ips: list = field(default_factory=list)
    os: str = ""
    cpu: int = 0
    ram_mb: int = 0
    disk_gb: int = 0
    tags: dict = field(default_factory=dict)
    owner: str = ""
    power_state: str = "unknown"
    location: str = ""