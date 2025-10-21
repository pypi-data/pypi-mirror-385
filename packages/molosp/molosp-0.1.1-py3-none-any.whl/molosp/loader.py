# Native
import sys
import os
import time
import traceback
from datetime import timedelta

# Third party
import boto3

# Local
from molosp.logger import logger


def load_external_module(spark_context, helper_module_s3_url, module_name):
    try:
        full_module_name = f"{module_name}.py"
        logger.info(f"Attempting to load module '{full_module_name}' from {helper_module_s3_url}")
        
        # Download the module file from S3 to a temporary location
        local_module_path = os.path.join('/tmp', full_module_name)
        s3_client = boto3.client('s3')
        logger.info(f"helper_module_s3_url: {helper_module_s3_url}")
        bucket_name, key = helper_module_s3_url.replace("s3://", "").split("/", 1)
        logger.info(f"Downloading {helper_module_s3_url} to {local_module_path}")
        s3_client.download_file(bucket_name, key, local_module_path)
        logger.info(f"Successfully downloaded helper module to {local_module_path}")
        
        # Add the downloaded file to SparkContext and sys.path
        spark_context.addPyFile(local_module_path)
        sys.path.insert(0, '/tmp')
        logger.info(f"Added {local_module_path} to SparkContext PyFiles")
        logger.info(f"Added /tmp to sys.path: {sys.path}")
        
        # Import the module
        start_import_time = time.time()
        module = __import__(module_name)  # Dynamic import
        end_import_time = time.time()
        logger.info(f"Successfully imported module '{full_module_name}'. Load time: {timedelta(seconds=end_import_time - start_import_time)}")
        return module
        
    except Exception as import_err:
        logger.error(f"Failed to import helper module: {str(import_err)}")
        logger.error(traceback.format_exc())
        raise