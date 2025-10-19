"""Tests for the S3CheckpointSaver class."""
import json
from unittest.mock import patch, MagicMock

import pytest

from s3checkpointer.s3saver import S3CheckpointSaver
from langgraph.checkpoint.base import CheckpointTuple


@pytest.mark.usefixtures("s3_client")
class TestS3CheckpointSaver:
    """Test suite for S3CheckpointSaver."""

    def test_init_and_setup(self, bucket_name, aws_credentials):
        """Test initialization and setup."""
        saver = S3CheckpointSaver(
            bucket_name=bucket_name,
            prefix="test-prefix",
            **aws_credentials
        )
        assert saver.bucket_name == bucket_name
        assert saver.prefix == "test-prefix"
        
        # Setup should create the bucket
        saver.setup()
        
        # Verify bucket exists by putting an object
        saver.s3.put_object(
            Bucket=bucket_name,
            Key="test-key",
            Body=b"test-content"
        )

    def test_put_and_get(self, s3_saver, sample_config, sample_checkpoint, sample_metadata):
        """Test putting and getting a checkpoint."""
        new_config = s3_saver.put(
            sample_config, 
            sample_checkpoint, 
            sample_metadata,
            new_versions={}
        )
        
        # Verify the new config has expected fields
        assert "configurable" in new_config
        assert "thread_id" in new_config["configurable"]
        assert "checkpoint_id" in new_config["configurable"]
        
        # Get the checkpoint using the new config
        result = s3_saver.get(new_config)
        assert result is not None
        
        config_result, checkpoint_result, metadata_result = result
        assert config_result["configurable"]["thread_id"] == sample_config["configurable"]["thread_id"]
        assert checkpoint_result == sample_checkpoint
        assert metadata_result == sample_metadata

    def test_get_tuple(self, s3_saver, sample_config, sample_checkpoint, sample_metadata):
        """Test getting a checkpoint tuple."""
        new_config = s3_saver.put(
            sample_config, 
            sample_checkpoint, 
            sample_metadata,
            new_versions={}
        )
        
        result = s3_saver.get_tuple(new_config)
        assert isinstance(result, CheckpointTuple)
        assert result.checkpoint == sample_checkpoint
        assert result.metadata == sample_metadata
        assert result.config["configurable"]["thread_id"] == sample_config["configurable"]["thread_id"]

    def test_list_checkpoints(self, s3_saver, sample_config, sample_metadata):
        """Test listing checkpoints."""
        # Create multiple checkpoints
        for i in range(1, 4):
            conf = s3_saver.put(
                sample_config, 
                {"index": i}, 
                sample_metadata,
                new_versions={}
            )
            print(i)
            print(conf)
        
        result = list(s3_saver.list(sample_config))
        assert len(result) == 3
        # Sort results by index to ensure consistent test results
        result.sort(key=lambda x: x.checkpoint["index"])
        assert result[0].checkpoint["index"] == 1
        assert result[2].checkpoint["index"] == 3

    def test_put_writes(self, s3_saver, sample_config, sample_writes):
        """Test storing pending writes."""
        # First create a checkpoint
        new_config = s3_saver.put(
            sample_config, 
            {"state": "initial"}, 
            {},
            new_versions={}
        )
        
        # Store writes for this checkpoint
        task_id = "test-task-id"
        s3_saver.put_writes(new_config, sample_writes, task_id)
        
        # Verify the writes were stored by checking S3 directly
        thread_id = new_config["configurable"]["thread_id"]
        checkpoint_id = new_config["configurable"]["checkpoint_id"]
        s3_key = f"{s3_saver.prefix}/{thread_id}/{checkpoint_id}_writes.json"
        
        response = s3_saver.s3.get_object(Bucket=s3_saver.bucket_name, Key=s3_key)
        data = json.loads(response["Body"].read().decode("utf-8"))
        
        assert data["writes"] == sample_writes
        assert data["task_id"] == task_id

    def test_delete_thread(self, s3_saver, sample_config, sample_metadata):
        """Test deleting a thread with checkpoints."""
        thread_id = sample_config["configurable"]["thread_id"]
        
        # Create multiple checkpoints
        for i in range(3):
            new_config = s3_saver.put(
                sample_config, 
                {"index": i}, 
                sample_metadata,
                new_versions={}
            )
            # Also create writes for each checkpoint
            s3_saver.put_writes(new_config, [{"op": i}], f"task-{i}")
        
        # Delete the thread
        s3_saver.delete_thread(thread_id)
        
        # Verify all objects are deleted by listing the prefix
        prefix = f"{s3_saver.prefix}/{thread_id}/"
        response = s3_saver.s3.list_objects_v2(
            Bucket=s3_saver.bucket_name,
            Prefix=prefix
        )
        
        # Should be empty
        assert "Contents" not in response or len(response["Contents"]) == 0

    def test_batch_deletion(self, s3_saver):
        """Test batch deletion in delete_thread method."""
        thread_id = "test-thread-id"
        
        # Mock a large number of objects
        with patch.object(s3_saver.s3, "get_paginator") as mock_paginator:
            # Create a mock paginator that returns a large number of objects
            mock_pages = [{"Contents": [{"Key": f"key{i}"} for i in range(1500)]}]
            mock_paginator.return_value.paginate.return_value = mock_pages
            
            # Mock delete_objects to verify it's called with batches
            with patch.object(s3_saver.s3, "delete_objects") as mock_delete:
                # Configure mock_delete to return a successful response
                mock_delete.return_value = {"Deleted": []}
                
                # Call the method being tested
                s3_saver.delete_thread(thread_id)
                
                # Should be called twice (1000 objects per batch)
                assert mock_delete.call_count == 2
                
                # Verify first batch has 1000 objects
                first_call_args = mock_delete.call_args_list[0][1]
                assert len(first_call_args["Delete"]["Objects"]) == 1000
                
                # Verify second batch has 500 objects
                second_call_args = mock_delete.call_args_list[1][1]
                assert len(second_call_args["Delete"]["Objects"]) == 500