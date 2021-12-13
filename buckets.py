"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage

# Create a GCP resource (Storage Bucket)
bucket = storage.Bucket('ynosidmetsa', name="ynosidmetsa", location="US")

# Export the DNS name of the bucket
pulumi.export('bucket_name', bucket.url)

init_sh = storage.BucketObject("initsh",
    name="init.sh",
    bucket=bucket.name,
    source=pulumi.FileAsset("init.sh")
)
