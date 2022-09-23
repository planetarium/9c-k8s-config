import json
import os
import tempfile
import time

import boto3
import botocore.exceptions


class S3File:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource("s3")
        assert bucket_name in [bucket.name for bucket in self.s3.buckets.all()]
        self.temp_dir = tempfile.TemporaryDirectory()

    def _load(self, filename: str) -> dict:
        temp_filepath = os.path.join(self.temp_dir.name, filename)

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Bucket.download_file
        bucket = self.s3.Bucket(self.bucket_name)
        bucket.download_file(filename, temp_filepath)

        with open(temp_filepath, "r") as f:
            data = json.load(f)

        return data

    def _save(self, filename: str, data: dict):
        temp_filepath = os.path.join(self.temp_dir.name, filename)

        with open(temp_filepath, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file
        self.s3.meta.client.upload_file(temp_filepath, self.bucket_name, filename)

    def update(self, filename: str, new_data: dict):
        data = self._load(filename)

        for key, value in new_data.items():
            data[key] = value

        self._save(filename, data)

    def copy(self, src_file: str, dst_file: str):
        copy_source = {"Bucket": self.bucket_name, "Key": src_file}
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy
        self.s3.meta.client.copy(copy_source, self.bucket_name, dst_file)

    def copy_from_bucket(self, src_file: str, dst_bucket: str, dst_key: str):
        copy_source = {"Bucket": self.bucket_name, "Key": src_file}
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.copy
        self.s3.meta.client.copy(copy_source, dst_bucket, dst_key)

    def check_if_dir_exist(self, dir_path: str):
        dir_path = dir_path.rstrip("/")
        bucket = self.s3.Bucket(self.bucket_name)
        return bool(list(bucket.objects.filter(Prefix=dir_path)))

    def get_files(self, dir_path: str):
        dir_path = dir_path.rstrip("/")
        dir_depth = len(dir_path.split(os.sep))
        file_list = []
        bucket = self.s3.Bucket(self.bucket_name)
        for object_summary in bucket.objects.filter(Prefix=dir_path):
            path = object_summary.key
            if path[-1] == "/":
                continue
            parts = path.split(os.sep)
            if len(parts) != dir_depth + 1:
                continue
            file_list.append(parts[-1])
        return file_list

    def delete(self, filepath: str):
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.delete_object
        self.s3.meta.client.delete_object(Bucket=self.bucket_name, Key=filepath)
        # = self.s3.Object(self.bucket_name, filepath).delete()

    def download(self, filepath: str, dir_path: str) -> str:
        filename = os.path.basename(filepath)
        dst_filepath = os.path.join(dir_path, filename)
        bucket = self.s3.Bucket(self.bucket_name)
        try:
            bucket.download_file(filepath, dst_filepath)
        except botocore.exceptions.ClientError as e:
            raise Exception(e, filepath)
        return dst_filepath

    def upload(self, filepath: str, dir_path: str) -> str:
        filename = os.path.basename(filepath)
        dst_filepath = os.path.join(dir_path, filename)
        bucket = self.s3.Bucket(self.bucket_name)
        try:
            bucket.upload_file(filepath, dst_filepath)
        except botocore.exceptions.ClientError as e:
            raise Exception(e, filepath)
        return dst_filepath


def create_invalidation(path_list):
    # cloudfront: d50mnk2u5fbcm.cloudfront.net, download.nine-chronicles.com, 9c-test.s3.amazonaws.com
    DISTRIBUTION_ID = "E1HPTSGY2RETN4"

    client = boto3.client("cloudfront")
    distributions = client.list_distributions()
    assert DISTRIBUTION_ID in [
        item["Id"] for item in distributions["DistributionList"]["Items"]
    ]

    items = [f"/{path}" for path in path_list]
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront.html#CloudFront.Client.create_invalidation
    response = client.create_invalidation(
        DistributionId=DISTRIBUTION_ID,
        InvalidationBatch={
            "Paths": {"Quantity": len(items), "Items": items},
            "CallerReference": str(time.time()).replace(".", ""),
        },
    )

    return response["Invalidation"]["Id"]


if __name__ == "__main__":
    _apv = "100082/6ec8E598962F1f475504F82fD5bF3410eAE58B9B/MEUCIQCYwrua7COV0DY181JT+RdciDSNAdxUyaDx8JvlKtpARwIgSRoxhfnqGW6UGD0K22HZbEnUB..bl5zeh.CZFidDL2Y=/ZHUxNjpXaW5kb3dzQmluYXJ5VXJsdTU2Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgyL1dpbmRvd3MuemlwdTE0Om1hY09TQmluYXJ5VXJsdTU3Omh0dHBzOi8vZG93bmxvYWQubmluZS1jaHJvbmljbGVzLmNvbS92MTAwMDgyL21hY09TLnRhci5nenU5OnRpbWVzdGFtcHUyNToyMDIxLTEwLTIyVDEyOjIxOjE0KzAwOjAwZQ=="
    _docker = "planetariumhq/ninechronicles-headless:git-cffc5fc294fbb8545c7ba684d4bcac1393405794"
    _version_windows_zip = "v100082/Windows.zip"

    _apv_json_file = "apv.json"
    _9c_launcher_config_json_file = "9c-launcher-config.json"
    _latest_windows_zip_file = "latest/Windows.zip"

    _bucket_name = "9c-test"
    _s3_file = S3File(_bucket_name)

    _apv_json_data = {"apv": _apv, "docker": _docker}
    _s3_file.update(_apv_json_file, _apv_json_data)

    _9c_launcher_config_json_data = {
        "AppProtocolVersion": _apv,
    }
    _s3_file.update(_9c_launcher_config_json_file, _9c_launcher_config_json_data)

    _s3_file.copy(_version_windows_zip, _latest_windows_zip_file)

    _path_list = [
        _apv_json_file,
        _9c_launcher_config_json_file,
        _latest_windows_zip_file,
    ]
    _invalidation_id = create_invalidation(_path_list)
    print("Invalidation created successfully with Id: " + _invalidation_id)
