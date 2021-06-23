'''
This is an example script that is used by a Glue job to import data from S3 to a DynamoDB table in the same account. Change the ApplyMapping.apply function with your schema details.

Prerequisites:

1. Run the crawler on the data in S3. This will create a logical table in a Glue Data Catalog Database
2. Replace the following parameters with your values:

    a- <GlueDatabaseName>
    b- <GlueTableName>
    c- <TargetRegion>
    d- <TargetDynamoDBTable>

'''

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job


args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Initialize the Dynamic frame using Glue Data Catalog DB and Table.  Replace <GlueDatabaseName> and <GlueTableName> with Glue DB and table names respectively

Source = glueContext.create_dynamic_frame.from_catalog(
    database="ft-versioning-migrated", table_name="taboneuyfa5m3jpmt7x4rhyqky_json_gz", transformation_ctx="Source")


# Map the source field names and data types to target values. The target values should be exactly the same as the source DyanmoDB table values
Mapped = ApplyMapping.apply(frame=Source, mappings=[
    ("item.createdAt.N", "string", "createdAt", "string"),
    ("item.expiredAt.N", "string", "expiredAt", "string"),
    ("item.id.S", "string", "id", "string"),
    ("item.owner.S", "string", "owner", "string"),
    ("item.retry.N", "string", "retry", "string"),
    ("item.status.S", "string", "status", "string"),
    ("item.version.N", "string", "version", "string")],
    transformation_ctx="Mapped")

# Write to target DynamoDB table. Replace <TargetRegion> and <TargetDynamoDBTable> with region and table name respectively
glueContext.write_dynamic_frame_from_options(
    frame=Mapped,
    connection_type="dynamodb",
    connection_options={"dynamodb.region": "ap-southeast-1",
                        "dynamodb.output.tableName": "ft-versioning-migrated",
                        "dynamodb.throughput.write.percent": "1.0"
                        }
)
job.commit()
