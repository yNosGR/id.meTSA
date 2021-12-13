import pulumi
import pulumi_gcp as gcp

import asg
import db as my_db

ynos = gcp.dns.ManagedZone("gcp-ynos-zone",
    description="ynos gcp DNS zone",
    dns_name="gcp.ynos.us.",
    )

testurl = gcp.dns.RecordSet("totallynotanlb",
    managed_zone=ynos.name,
    name="lbtest.gcp.ynos.us.",
    rrdatas=[asg.my_forwarding_rule.ip_address],
    ttl=300,
    type="A",
)

dburl = gcp.dns.RecordSet("mytestdb",
    managed_zone=ynos.name,
    name="idmetsadb.gcp.ynos.us.",
    rrdatas=[my_db.instance.first_ip_address],
    ttl=300,
    type="A",
)

pulumi.export('testurl', testurl.name)
pulumi.export('dburl', dburl.name)
