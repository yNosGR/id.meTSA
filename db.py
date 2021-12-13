import pulumi
import pulumi_gcp as gcp

import network as my_networks
import dns

private_ip_address = gcp.compute.GlobalAddress("privateipaddress",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    prefix_length=16,
    network=my_networks.asg_network.network,
)

private_vpc_connection = gcp.servicenetworking.Connection("privatevpcconnection",
    network=my_networks.asg_network.network,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip_address.name],
)

#db_name_suffix = random.RandomId("dbNameSuffix", byte_length=4)

instance = gcp.sql.DatabaseInstance("instance",
    
    region="us-east1",
    database_version="MYSQL_5_7",
    deletion_protection=False,
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-f1-micro",
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,
            private_network=my_networks.asg_network.network,
        ),
    ),
    opts=pulumi.ResourceOptions( depends_on=[private_vpc_connection])
)



users = gcp.sql.User("dontuserthisuser",
    name="dontusethisuser",
    instance=instance.name,
    password="pleasedontusethishorriblepassword"
)

pulumi.export('instance ', instance.first_ip_address)
