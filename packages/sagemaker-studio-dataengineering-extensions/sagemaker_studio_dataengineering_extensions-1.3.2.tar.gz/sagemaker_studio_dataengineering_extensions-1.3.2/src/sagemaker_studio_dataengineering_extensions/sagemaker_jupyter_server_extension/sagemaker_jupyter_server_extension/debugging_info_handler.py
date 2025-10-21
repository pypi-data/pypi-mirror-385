import json
import logging
import os
import uuid
 
import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
from tornado import web
from sagemaker_studio_metrics_collector.common_logging import async_with_metrics

logger = logging.getLogger(__name__)
SUCCESS_FILE_NAME = ".success"
DEBUGGING_INFO_FILE_NAME = "debugging_info.json"

class SageMakerConnectionDebuggingInfoHandler(ExtensionHandlerMixin, APIHandler):
    @tornado.web.authenticated
    @async_with_metrics("GetDebuggingInfo", extension_name="server_extension")
    async def get(self, cell_id):
        response = {}
        
        # Validate that cell_id is a valid UUID
        try:
            uuid_obj = uuid.UUID(cell_id)
            # Ensure the string representation matches the input to prevent non-standard formats
            if str(uuid_obj) != cell_id:
                logger.error(f"Invalid UUID format: {cell_id}")
                self.set_status(400)
                self.finish(json.dumps({"error": "Invalid cell_id format."}))
                return
        except ValueError:
            logger.error(f"Invalid UUID: {cell_id}")
            self.set_status(400)
            self.finish(json.dumps({"error": "Invalid cell id."}))
            return
        
        # Determine the debugging directory based on available paths
        src_path = os.path.expanduser("~/src")
        shared_path = os.path.expanduser("~/shared")
        
        if os.path.exists(src_path):
            debugging_info_folder = os.path.join(src_path, f".temp_sagemaker_unified_studio_debugging_info/{cell_id}")
        elif os.path.exists(shared_path):
            debugging_info_folder = os.path.join(shared_path, f".temp_sagemaker_unified_studio_debugging_info/{cell_id}")
        else:
            logger.error("Neither ~/src nor ~/shared directories exist")
            self.set_status(404)
            self.finish(json.dumps({"error": "Cannot find debugging path."}))
            return
        logger.info(f"Trying to get debugging info from path {debugging_info_folder}")
        try:
            if not os.path.exists(debugging_info_folder):
                logger.error(f"Debugging info folder: {debugging_info_folder} does not exist")
                self.set_status(404)
                self.finish(json.dumps({"error": f"Cannot find debugging path."}))
                return
            else:
                success_file = os.path.join(debugging_info_folder, SUCCESS_FILE_NAME)
                debugging_file = os.path.join(debugging_info_folder, DEBUGGING_INFO_FILE_NAME)
                if os.path.exists(success_file) and os.path.exists(debugging_file):
                    logger.info(f"Debugging info under folder: {debugging_info_folder} is ready")
                    response["status"] = "ready"
                    self.finish(json.dumps(response))
                elif not os.path.exists(success_file) and os.path.exists(debugging_file):
                    logger.info(f"Debugging info under folder: {debugging_info_folder} is generating in progress")
                    response["status"] = "in_progress"
                    self.finish(json.dumps(response))
                else:
                    logger.error(f"Debugging file under folder: {debugging_info_folder} is removed")
                    self.set_status(404)
                    self.finish(json.dumps({"error": f"Debugging file has been removed."}))
        except Exception as e:
            logger.exception(e)
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))
