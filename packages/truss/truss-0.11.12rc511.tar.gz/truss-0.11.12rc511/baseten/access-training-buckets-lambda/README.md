# Access Training Buckets

NOTE: this is not a python package. The contents of this folder should not be imported in other python projects.

The `lambda_function.py` is the function that is deployed to AWS Lambda that is used to enable creation and access of training buckets.

It is deployed to lambda via zip, by running `zip -r lambda_function.zip lambda_function.py` and uploading to AWS Lambda.

It relies on the role `TrainingCheckpointsLambda` which has the `LambdaGetOrCreateTrainingBucketAndRole` policy. 
