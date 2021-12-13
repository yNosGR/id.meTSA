import pulumi
import pulumi_gcp as gcp

import network as my_networks

private_ip_alloc = gcp.compute.GlobalAddress("privateIpAlloc",
    address="10.3.0.128",
    name="privatedb",
    purpose="PRIVATE_SERVICE_CONNECT",
    address_type="INTERNAL",
    network=my_networks.asg_network.network)

foobar = gcp.servicenetworking.Connection("foobar",
    network=my_networks.asg_network.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[my_networks.asg_network.ip_cidr_range,"10.3.0.0/24"]
)

#instance = gcp.sql.DatabaseInstance("instance",
#    region="us-east1",
#    database_version="MYSQL_5_7",
#    settings=gcp.sql.DatabaseInstanceSettingsArgs(
#        tier="db-f1-micro",
#        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
#          ipv4_enabled=False,
#          private_network=my_networks.subnet_db.id,
#        ),
#    ),
#)

#database = gcp.sql.Database("database", instance=instance.name)

#users = gcp.sql.User("dontuserthisuser",
#    name="dontusethisuser",
#    instance=instance.name,
#    password="pleasedontusethishorriblepassword"
#)

#pulumi.export('instance ', instance.first_ip_address)
