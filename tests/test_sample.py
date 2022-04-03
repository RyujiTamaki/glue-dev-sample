import pytest
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
import sys
from src import sample


@pytest.fixture(scope="module", autouse=True)
def glue_context():
    sys.argv.append('--JOB_NAME')
    sys.argv.append('test_count')

    args = getResolvedOptions(sys.argv, ['JOB_NAME'])
    sc = SparkSession.builder.getOrCreate()
    sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "http://glue.dev.s3.local:4566")
    sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    sc._jsc.hadoopConfiguration().set("fs.s3a.signing-algorithm", "S3SignerType")
    sc._jsc.hadoopConfiguration().set("fs.s3a.change.detection.mode", "None")
    sc._jsc.hadoopConfiguration().set("fs.s3a.change.detection.version.required", "false")
    context = GlueContext(sc)
    job = Job(context)
    job.init(args['JOB_NAME'], args)

    yield(context)

    job.commit()


def test_counts(glue_context):
    dyf = sample.read_json(glue_context, "s3://awsglue-datasets/examples/us-legislators/all/persons.json")
    assert dyf.toDF().count() == 1961