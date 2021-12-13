import pulumi
import pulumi_gcp as gcp

import dns
import buckets as my_buckets
import network as my_networks

debian10 = gcp.compute.get_image(family="debian-10",
    project="debian-cloud")

default_instance_template = gcp.compute.InstanceTemplate("defaultinstancetemplate",
    region=my_networks.my_region,
    machine_type="e2-micro",
    can_ip_forward=False,
    metadata_startup_script="gsutil cp gs://ynosidmetsa/init.sh . &&  chmod +x init.sh && ./init.sh && rm init.sh",
    tags=[
        "foo",
        "baz",
    ],
    disks=[gcp.compute.InstanceTemplateDiskArgs(
        source_image=debian10.id,
    )],
    network_interfaces=[gcp.compute.InstanceTemplateNetworkInterfaceArgs(
        network=my_networks.subnet_asg.name,
        subnetwork=my_networks.asg_network.name
    )],
    metadata={
        "foo": "bar",
        "baz": "qux",
    },
    service_account=gcp.compute.InstanceTemplateServiceAccountArgs(
        scopes=[
            "userinfo-email",
            "compute-ro",
            "storage-ro",
        ],
    ),
    #opts=pulumi.ResourceOptions(provider=google_beta)
)

http_health_check = gcp.compute.HttpHealthCheck("http-health-check",
  name="http-health-check",
  port=80,
  request_path="/index.html",
)

default_target_pool = gcp.compute.TargetPool("defaulttargetpool",
  health_checks=http_health_check.name,
  region=my_networks.my_region,
)


autohealing = gcp.compute.HealthCheck("autohealing",
    check_interval_sec=5,
    timeout_sec=5,
    healthy_threshold=2,
    unhealthy_threshold=10,
    http_health_check=gcp.compute.HealthCheckHttpHealthCheckArgs(
        request_path="/index.html",
        port=80,
    ))

default_instance_group_manager = gcp.compute.InstanceGroupManager("defaultinstancegroupmanager",
    zone="us-east1-b",
    versions=[gcp.compute.InstanceGroupManagerVersionArgs(
        instance_template=default_instance_template.id,
        name="primary",
    )],
    named_ports=[gcp.compute.InstanceGroupManagerNamedPortArgs(
        name="http",
        port=80,
    )],
    auto_healing_policies=gcp.compute.InstanceGroupManagerAutoHealingPoliciesArgs(
        health_check=autohealing.id,
        initial_delay_sec=300,
    ),
    target_pools=[default_target_pool.id],
    base_instance_name="autoscaler-sample",
    #opts=pulumi.ResourceOptions(provider=google_beta)
)

default_autoscaler = gcp.compute.Autoscaler("defaultautoscaler",
    zone="us-east1-b",
    target=default_instance_group_manager.id,
    autoscaling_policy=gcp.compute.AutoscalerAutoscalingPolicyArgs(
        max_replicas=5,
        min_replicas=1,
        cooldown_period=60,
        cpu_utilization=gcp.compute.AutoscalerAutoscalingPolicyCpuUtilizationArgs(
            target=0.8,
    )),
    #opts=pulumi.ResourceOptions(provider=google_beta)
)

default_backend_service = gcp.compute.BackendService("defaultbackendservice",
    protocol="HTTP",
    backends=[gcp.compute.BackendServiceBackendArgs(
        balancing_mode="UTILIZATION",
        capacity_scaler=1,
        group=default_instance_group_manager.instance_group
    )],
    connection_draining_timeout_sec=300,
    description="test",
    health_checks=autohealing.id,
    load_balancing_scheme="EXTERNAL",
)    

urlmap = gcp.compute.URLMap("testurlmap",
    description="a description",
    default_service=default_backend_service.id,
)

default_target_http_proxy = gcp.compute.TargetHttpProxy("defaulttargethttpproxy", url_map=urlmap.id)

my_forwarding_rule = gcp.compute.GlobalForwardingRule("googlecomputeforwardingrule",
    #backend_service=default_backend_service.id,
    #region=my_networks.my_region,
    target=default_target_http_proxy.id,
    port_range="80",
    load_balancing_scheme="EXTERNAL",
#    allow_global_access=True,
)   
 
pulumi.export('forwarding_rule ip_address', my_forwarding_rule.ip_address)
