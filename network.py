import pulumi

import pulumi_gcp as gcp

my_region="us-east1"

#create the network definitions
subnet_asg = gcp.compute.Network("net-asg", name="net-asg", auto_create_subnetworks=False)
subnet_db = gcp.compute.Network("net-db", name="net-db", auto_create_subnetworks=False)

#define the subnet on the networks
#going with a /24 to keep it easy to organize.
asg_network = gcp.compute.Subnetwork("first-autoscaler-network",
      name="asg-network",
      ip_cidr_range="10.3.1.0/24",
      region="us-east1",
      purpose="PRIVATE",
      network=subnet_asg.id,
    )

db_network = gcp.compute.Subnetwork("first-db-network",
      name="db-network",
      ip_cidr_range="10.3.2.0/24",
      region=my_region,
      purpose="PRIVATE",
      network=subnet_db.id,
    )

asg_router = gcp.compute.Router("asg-router",
    region=my_region,
    network=subnet_asg.id
    )

asg_nat = gcp.compute.RouterNat("nat",
    router=asg_router.name,
    region=asg_router.region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES",
    log_config=gcp.compute.RouterNatLogConfigArgs(
        enable=True,
        filter="ERRORS_ONLY",
    ))

# allow all access from IAP and health check ranges
default_firewall = gcp.compute.Firewall("asg-ssh",
    direction="INGRESS",
    network=subnet_asg.name,
    source_ranges=[
        "130.211.0.0/22",
        "35.191.0.0/16",
        "35.235.240.0/20",
    ],
    allows=[gcp.compute.FirewallAllowArgs(
        protocol="tcp",
    )],
    #opts=pulumi.ResourceOptions(provider=google_beta)
)

#pulumi.export('asg_network ', asg_network)
