import json
import os
import uuid
from unittest.mock import patch, MagicMock

import pytest
import tornado.httpclient
from sagemaker_jupyter_server_extension.debugging_info_handler import (
    SageMakerConnectionDebuggingInfoHandler,
    SUCCESS_FILE_NAME,
    DEBUGGING_INFO_FILE_NAME,
)

# Helper function to get the debugging directory path for tests
def get_debugging_dir_path(cell_id):
    """
    Mock function to get the debugging directory path for tests.
    In tests, we'll always use the src path.
    """
    return os.path.join(os.path.expanduser("~/src"), f".temp_sagemaker_unified_studio_debugging_info/{cell_id}")


async def test_debugging_info_handler_invalid_uuid(jp_fetch):
    """Test when cell_id is not a valid UUID."""
    cell_id = "not-a-uuid"
    
    # When
    with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
        await jp_fetch("api", "debugging", "info", cell_id)
    
    # Then
    assert excinfo.value.code == 400
    response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
    assert response_json == {"error": "Invalid cell id."}


async def test_debugging_info_handler_folder_not_exists(jp_fetch):
    """Test when debugging folder doesn't exist."""
    cell_id = str(uuid.uuid4())
    
    with patch('os.path.exists', return_value=False):
        # When
        with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
            await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert excinfo.value.code == 404
        response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
        assert response_json == {"error": f"Cannot find debugging path."}


async def test_debugging_info_handler_ready_state(jp_fetch):
    """Test when both success file and debugging file exist."""
    cell_id = str(uuid.uuid4())
    
    def path_exists_side_effect(path):
        # First check is for os.path.exists("~/src")
        if path == os.path.expanduser("~/src"):
            return True
        # Second check is for os.path.exists("~/shared") - should not be called
        elif path == os.path.expanduser("~/shared"):
            return False
        # Third check is for the debugging directory
        elif path == get_debugging_dir_path(cell_id):
            return True
        # Fourth and fifth checks are for the success and debugging files
        elif path.endswith(SUCCESS_FILE_NAME) or path.endswith(DEBUGGING_INFO_FILE_NAME):
            return True
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        response = await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert response.code == 200
        payload = json.loads(response.body)
        assert payload == {"status": "ready"}


async def test_debugging_info_handler_in_progress_state(jp_fetch):
    """Test when only debugging file exists but success file doesn't."""
    cell_id = str(uuid.uuid4())
    
    def path_exists_side_effect(path):
        # First check is for os.path.exists("~/src")
        if path == os.path.expanduser("~/src"):
            return True
        # Second check is for os.path.exists("~/shared") - should not be called
        elif path == os.path.expanduser("~/shared"):
            return False
        # Third check is for the debugging directory
        elif path == get_debugging_dir_path(cell_id):
            return True
        # Fourth check is for the success file
        elif path.endswith(SUCCESS_FILE_NAME):
            return False
        # Fifth check is for the debugging file
        elif path.endswith(DEBUGGING_INFO_FILE_NAME):
            return True
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        response = await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert response.code == 200
        payload = json.loads(response.body)
        assert payload == {"status": "in_progress"}


async def test_debugging_info_handler_files_removed(jp_fetch):
    """Test when debugging folder exists but files are removed."""
    cell_id = str(uuid.uuid4())
    
    def path_exists_side_effect(path):
        # First check is for os.path.exists("~/src")
        if path == os.path.expanduser("~/src"):
            return True
        # Second check is for os.path.exists("~/shared") - should not be called
        elif path == os.path.expanduser("~/shared"):
            return False
        # Third check is for the debugging directory
        elif path == get_debugging_dir_path(cell_id):
            return True
        # Fourth and fifth checks are for the success and debugging files
        elif path.endswith(SUCCESS_FILE_NAME) or path.endswith(DEBUGGING_INFO_FILE_NAME):
            return False
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
            await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert excinfo.value.code == 404
        response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
        assert response_json == {"error": "Debugging file has been removed."}


async def test_debugging_info_handler_exception(jp_fetch):
    """Test when an exception occurs during processing."""
    cell_id = str(uuid.uuid4())
    
    # Create a side effect function that raises an exception only after the directory checks
    def path_exists_side_effect(path):
        # First check is for os.path.exists("~/src")
        if path == os.path.expanduser("~/src"):
            return True
        # Second check is for os.path.exists("~/shared") - should not be called
        elif path == os.path.expanduser("~/shared"):
            return False
        # Third check is for the debugging directory - this is where we'll raise the exception
        elif path == get_debugging_dir_path(cell_id):
            raise Exception("Test exception")
        return False
    
    with patch('os.path.exists', side_effect=path_exists_side_effect):
        # When
        with pytest.raises(tornado.httpclient.HTTPClientError) as excinfo:
            await jp_fetch("api", "debugging", "info", cell_id)
        
        # Then
        assert excinfo.value.code == 500
        response_json = json.loads(excinfo.value.response.body.decode('utf-8'))
        assert "error" in response_json
        assert "Test exception" in response_json["error"]
