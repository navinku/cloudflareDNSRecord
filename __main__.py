import pulumi
import pulumi_cloudflare as cloudflare
import yaml
import time
from pathlib import Path
from pulumi.log import warn, error

config = pulumi.Config()
cloudflare_config = config.require_object("cloudflare")

cloudflare_provider = cloudflare.Provider(
    "cloudflare-provider",
    api_token=cloudflare_config.get("apiToken"),
    opts=pulumi.ResourceOptions(version="5.49.1")
)

def load_dns_records(record_type):
    try:
        with open(f"resources/{record_type}.yaml") as f:
            records = yaml.safe_load(f) or []
            for record in records:
                if 'name' not in record:
                    raise ValueError(f"Record missing required field 'name' in {record_type}.yaml")
                if not record.get('content') and not record.get('value'):
                    raise ValueError(f"Record {record['name']} missing 'content' or 'value'")
            return records
    except FileNotFoundError:
        warn(f"No {record_type} records file found at resources/{record_type}.yaml")
        return []
    except Exception as e:
        error(f"Error loading {record_type}.yaml: {str(e)}")
        return []

def create_dns_record(record_type, record):
    record_name = record['name']
    content = record.get('content') or record.get('value')
    record_type = record.get('type', record_type.upper().replace('RECORD', ''))
    proxied = record.get('proxied', False)
    ttl = 1 if proxied else record.get('ttl', 300)
    zone_id = cloudflare_config.get("zoneId")
    
    try:
        existing = cloudflare.Record.get(
            f"{record_type}-{record_name.replace('.', '-')}-check",
            f"{zone_id}/{record_type}/{record_name}",
            opts=pulumi.ResourceOptions(provider=cloudflare_provider)
        )
        warn(f"Record {record_name} ({record_type}) already exists - skipping creation")
        return None
    except:
        try:
            return cloudflare.Record(
                f"{record_type}-{record_name.replace('.', '-')}",
                zone_id=zone_id,
                name=record_name,
                type=record_type,
                content=content,
                ttl=ttl,
                proxied=proxied,
                comment=record.get('comment', "Managed by Pulumi"),
                opts=pulumi.ResourceOptions(
                    provider=cloudflare_provider,
                    ignore_changes=["comment"]
                )
            )
        except Exception as e:
            error(f"Failed to create record {record_name}: {str(e)}")
            return None

def create_dns_records(record_type):
    records = load_dns_records(record_type)
    successful_records = 0
    
    for record in records:
        result = create_dns_record(record_type, record)
        if result:
            successful_records += 1
    
    if successful_records > 0:
        pulumi.export(f"{record_type}_records_created", successful_records)
    elif records:  
        warn(f"No {record_type} records were processed successfully")

create_dns_records("arecord")
create_dns_records("cname")