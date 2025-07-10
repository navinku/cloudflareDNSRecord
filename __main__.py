import pulumi
import pulumi_cloudflare as cloudflare

config = pulumi.Config()
cloudflare_config = config.require_object("cloudflare")

cloudflare_provider = cloudflare.Provider(
    "cloudflare-provider",
    api_token=cloudflare_config.get("apiToken")  # Get from object
)

dns_record = cloudflare.Record(
    "example-dns-record",
    zone_id=cloudflare_config.get("zoneId"),
    name="example",
    type="A",
    content="192.0.2.1",
    ttl=1,
    proxied=True,
    comment="Managed by Pulumi",
    opts=pulumi.ResourceOptions(provider=cloudflare_provider)
)