"""Module for saving checkpoints to S3."""
import json
from datetime import datetime
from typing import Iterator
from uuid import uuid4

import boto3
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_metadata,
)


class S3CheckpointSaver(BaseCheckpointSaver):
    """A checkpoint saver that stores checkpoints in an S3 bucket.

    Parameters
    ----------
    bucket_name : str
        The name of the S3 bucket.
    prefix : str, optional
        A prefix to use for all keys in the bucket, by default "".
    aws_access_key_id : str, optional
        The AWS access key ID, by default None.
    aws_secret_access_key : str, optional
        The AWS secret access key, by default None.
    region_name : str, optional
        The AWS region name, by default None.
    """

    def __init__(
        self,
        bucket_name: str,
        prefix: str = "",
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str | None = None,
    ):
        """Initialize the S3CheckpointSaver.

        Args:
            bucket_name: The name of the S3 bucket.
            prefix: A prefix to use for all keys in the bucket.
            aws_access_key_id: The AWS access key ID. If not provided, it will be
                read from the environment or ~/.aws/credentials.
            aws_secret_access_key: The AWS secret access key. If not provided, it will be
                read from the environment or ~/.aws/credentials.
            region_name: The AWS region name. If not provided, it will be
                read from the environment or ~/.aws/credentials.
        """
        super().__init__()
        client_kwargs = {}
        if aws_access_key_id:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if region_name:
            client_kwargs["region_name"] = region_name

        self.s3 = boto3.client("s3", **client_kwargs)
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/")

    def setup(self) -> None:
        """Create bucket if needed."""
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except self.s3.exceptions.ClientError:
            self.s3.create_bucket(Bucket=self.bucket_name)

    def put(
        self, 
        config: dict, 
        checkpoint: Checkpoint, 
        metadata: CheckpointMetadata,
        new_versions: dict
    ) -> dict:
        """Save a checkpoint to the S3 bucket.

        Parameters
        ----------
        config : dict
            The configuration for the checkpoint.
        checkpoint : Checkpoint
            The checkpoint to save.
        metadata : CheckpointMetadata
            The metadata for the checkpoint.
        new_versions : dict
            Version information for the checkpoint.

        Returns
        -------
        dict
            The configuration for the saved checkpoint.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = str(uuid4())
        timestamp = datetime.utcnow().isoformat()
        serialized_metadata = get_checkpoint_metadata(checkpoint, metadata)

        new_config = {
            "configurable": {
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
                "thread_id": thread_id,
                "timestamp": timestamp,
            }
        }

        parent_checkpoint = config["configurable"].get("checkpoint_id")

        data = {
            "config": new_config,
            "checkpoint": checkpoint,
            "parent_checkpoint": parent_checkpoint,
            "metadata": serialized_metadata,
            "created_at": timestamp,
        }

        s3_key = f"{self.prefix}/{thread_id}/{checkpoint_id}.json" if self.prefix else f"{thread_id}/{checkpoint_id}.json"

        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=json.dumps(data, default=str).encode('utf-8')
        )

        return new_config
    
    def get_tuple(self, config: dict) -> CheckpointTuple | None:
        """Get a checkpoint tuple from the S3 bucket.

        Parameters
        ----------
        config : dict
            The configuration for the checkpoint to retrieve.

        Returns
        -------
        CheckpointTuple | None
            A CheckpointTuple containing the checkpoint configuration, the checkpoint itself,
            the checkpoint metadata, and parent config, or None if the checkpoint is not found.
        """
        result = self.get(config)
        if result is None:
            return None
        
        checkpoint_config, checkpoint, metadata = result

        parent_config = None
        if "parent_checkpoint" in checkpoint_config.get("configurable", {}):
            parent_checkpoint_id = checkpoint_config["configurable"]["parent_checkpoint"]
            if parent_checkpoint_id:
                parent_config = {
                    "configurable": {
                        "thread_id": config["configurable"]["thread_id"],
                        "checkpoint_id": parent_checkpoint_id,
                    }
                }
        
        return CheckpointTuple(
            config=checkpoint_config,
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent_config,
        )
    
    def get(self, config: dict) -> tuple[dict, Checkpoint, CheckpointMetadata] | None:
        """Get a checkpoint from the S3 bucket.

        Parameters
        ----------
        config : dict
            The configuration for the checkpoint to retrieve.

        Returns
        -------
        tuple[dict, Checkpoint, CheckpointMetadata] | None
            A tuple containing the checkpoint configuration, the checkpoint itself,
            and the checkpoint metadata, or None if the checkpoint is not found.
        """
        thread_id = config["configurable"]["thread_id"]
        if "checkpoint_id" in config["configurable"]:
            checkpoint_id = config["configurable"]["checkpoint_id"]
            s3_key = f"{self.prefix}/{thread_id}/{checkpoint_id}.json" if self.prefix else f"{thread_id}/{checkpoint_id}.json"
            try:
                response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
                body = response['Body'].read().decode('utf-8')
                data = json.loads(body)

                return (
                    data["config"],
                    data["checkpoint"],
                    data["metadata"],
                )
            except self.s3.exceptions.NoSuchKey:
                return None

        prefix = f"{self.prefix}/{thread_id}/" if self.prefix else f"{thread_id}/"
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name, 
                Prefix=prefix
            )

            if "Contents" not in response or len(response["Contents"]) == 0:
                return None

            latest = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]
            
            obj_response = self.s3.get_object(Bucket=self.bucket_name, Key=latest["Key"])
            data = json.loads(obj_response["Body"].read().decode('utf-8'))
            checkpoint_id = latest["Key"].split("/")[-1].replace(".json", "")
            
            config_result = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": checkpoint_id,
                }
            }
            return config_result, data["checkpoint"], data["metadata"]
        except Exception:
            return None

    def list(
        self,
        config: dict | None = None,
        *,
        limit: int = 10,
        before: dict | None = None,
        **kwargs,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the S3 bucket.

        Parameters
        ----------
        config : dict, optional
            The configuration to filter checkpoints, by default None.
        limit : int, optional
            The maximum number of checkpoints to return, by default 10.
        before : dict, optional
            A configuration to list checkpoints before, by default None.

        Returns
        -------
        iter[CheckpointTuple]
            An iterator of checkpoint tuples.
        """
        if not config or "configurable" not in config:
            return iter([])

        thread_id = config["configurable"]["thread_id"]
        prefix = f"{self.prefix}/{thread_id}/" if self.prefix else f"{thread_id}/"
        
        try:
            paginator = self.s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(
                Bucket=self.bucket_name, 
                Prefix=prefix, 
                PaginationConfig={"MaxItems": limit or 1000}
            )

            items = []
            for page in pages:
                if "Contents" not in page:
                    continue
                for obj in sorted(page["Contents"], key=lambda x: x["LastModified"], reverse=True):
                    try:
                        response = self.s3.get_object(Bucket=self.bucket_name, Key=obj["Key"])
                        data = json.loads(response["Body"].read().decode('utf-8'))
                        checkpoint_id = obj["Key"].split("/")[-1].replace(".json", "")
                        
                        checkpoint_config = {
                            "configurable": {
                                "thread_id": thread_id,
                                "checkpoint_id": checkpoint_id,
                            }
                        }
                        
                        parent_config = None
                        if data.get("parent_checkpoint"):
                            parent_config = {
                                "configurable": {
                                    "thread_id": thread_id,
                                    "checkpoint_id": data["parent_checkpoint"],
                                }
                            }
                        
                        items.append(
                            CheckpointTuple(
                                config=checkpoint_config,
                                checkpoint=data["checkpoint"],
                                metadata=data["metadata"],
                                parent_config=parent_config,
                            )
                        )
                    except Exception:
                        continue
            
            if before:
                before_id = before["configurable"]["checkpoint_id"]
                items = [item for item in items if item.config["configurable"]["checkpoint_id"] != before_id]

            return iter(items[:limit])
        except Exception:
            return iter([])

    def put_writes(
        self,
        config: dict,
        writes: list,
        task_id: str
    ) -> None:
        """Store pending writes for a checkpoint.

        Parameters
        ----------
        config : dict
            The configuration for the checkpoint.
        writes : list
            List of pending writes to store.
        task_id : str
            The task ID associated with the writes.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        
        writes_data = {
            "writes": writes,
            "task_id": task_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        s3_key = f"{self.prefix}/{thread_id}/{checkpoint_id}_writes.json" if self.prefix else f"{thread_id}/{checkpoint_id}_writes.json"
        
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(writes_data, default=str).encode('utf-8')
            )
        except Exception:
             pass

    def delete_thread(self, thread_id: str) -> None:
        """Delete all checkpoints and writes associated with a specific thread ID.

        Parameters
        ----------
        thread_id : str
            The thread ID whose checkpoints and writes should be deleted.
        """
        prefix = f"{self.prefix}/{thread_id}/" if self.prefix else f"{thread_id}/"
        
        try:
            paginator = self.s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
            
            objects_to_delete = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        objects_to_delete.append({"Key": obj["Key"]})

            if objects_to_delete:
                batch_size = 1000
                for i in range(0, len(objects_to_delete), batch_size):
                    batch = objects_to_delete[i:i + batch_size]
                    self.s3.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={"Objects": batch}
                    )
        except Exception:
            pass
