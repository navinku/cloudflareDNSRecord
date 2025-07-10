import pulumi
import pulumi_cloudflare as cloudflare

config = pulumi.Config()
cloudflare_config = config.require_object("cloudflare")

cloudflare_provider = cloudflare.Provider(
    "cloudflare-provider",
    api_token=cloudflare_config.get("apiToken")
)

dns_record = cloudflare.Record(
    "example-dns-record",
    zone_id=cloudflare_config.get("zoneId"),  # Get zone ID from config
    name="example",
    type="A",
    value="192.0.2.1",
    ttl=3600,
    comment="Managed by Pulumi",
    opts=pulumi.ResourceOptions(provider=cloudflare_provider)
)

pulumi.export("dns_record_id", dns_record.id)
pulumi.export("dns_record_fqdn", dns_record.hostname)