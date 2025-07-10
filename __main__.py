import pulumi
import pulumi_cloudflare as cloudflare
import yaml
from pathlib import Path

config = pulumi.Config()
cloudflare_config = config.require_object("cloudflare")

cloudflare_provider = cloudflare.Provider(
    "cloudflare-provider",
    api_token=cloudflare_config.get("apiToken"),  # Get from object
    opts=pulumi.ResourceOptions(version="4.0.0")
)

def load_dns_records(record_type):
    records = []
    try:
        with open(f"resources/{record_type}.yaml") as f:
            records = yaml.safe_load(f) or []
    except FileNotFoundError:
        pulumi.log.warn(f"No {record_type} records file found at resources/{record_type}.yaml")
    return records

def create_dns_records(record_type):
    records = load_dns_records(record_type)
    for record in records:
        cloudflare.Record(
            f"{record_type}-{record['name']}",
            zone_id=cloudflare_config.get("zoneId"),
            name=record['name'],
            type=record_type.upper(),  # A or CNAME
            value=record.get('content') or record.get('value'),
            ttl=record.get('ttl', 1),
            proxied=record.get('proxied', True),
            comment=record.get('comment', "Managed by Pulumi"),
            opts=pulumi.ResourceOptions(provider=cloudflare_provider)
        )

create_dns_records("arecord")
create_dns_records("cname")