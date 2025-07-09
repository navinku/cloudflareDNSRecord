"""A Python Pulumi program for managing Cloudflare DNS records"""

import pulumi
import pulumi_cloudflare as cloudflare

# Example: Create a DNS record
# Replace with your actual zone and record configuration
dns_record = cloudflare.Record(
    "example-dns-record",
    zone_id="your-zone-id",  # Replace with your Cloudflare zone ID
    name="example",
    type="A",
    value="192.0.2.1",
    ttl=3600,
    comment="Managed by Pulumi"
)

# Export the record ID
pulumi.export("dns_record_id", dns_record.id)
pulumi.export("dns_record_fqdn", dns_record.hostname)