import json
import logging
import os
from jupyter_server.base.handlers import APIHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin
import tornado

logger = logging.getLogger(__name__)

class TelemetryHandler(ExtensionHandlerMixin, APIHandler):
    """
    Handler for business intelligence metrics.
    Receives telemetry data from frontend and saves it in CloudWatch compatible format.
    """

    def serialize_to_cloudwatch_format(self, data):
        """
        Serialize telemetry data to CloudWatch Embedded Metric Format (EMF).
        """
        metrics = {
            "_aws": {
                "Timestamp": data.get("timestamp", None),
                "CloudWatchMetrics": [{
                    "Namespace": "SageMakerUnifiedStudio",
                    "Dimensions": [["Operation", "Context"]],
                    "Metrics": [
                        {"Name": "Occurrence", "Unit": "Count"}
                    ]
                }]
            }
        }

        if "payload" in data:
            payload = data["payload"]

            # Set dimensions
            metrics["Operation"] = payload.get("eventType", "Unknown")
            metrics["Context"] = payload.get("eventContext", "Unknown")

            # Handle latency if present
            if "latency" in payload:
                metrics["_aws"]["CloudWatchMetrics"][0]["Metrics"].append(
                    {"Name": "Latency", "Unit": "Milliseconds"}
                )
                metrics["Latency"] = payload["latency"]

            # Set properties if they exist in payload
            if "eventDetail" in payload:
                metrics["EventDetail"] = payload["eventDetail"]
            if "eventValue" in payload:
                metrics["EventValue"] = payload["eventValue"]
            if "funnel" in payload:
                metrics["Funnel"] = payload["funnel"]
            if "taskId" in payload:
                metrics["TaskId"] = payload["taskId"]

            metrics["Occurrence"] = 1

        return metrics


    @tornado.web.authenticated
    async def post(self):
        """
        Handle POST requests containing telemetry data.

        The handler:
        1. Receives JSON payload from frontend
        2. Serializes it to CloudWatch format
        3. Writes to local log file for later processing

        Raises:
            HTTPError(500) if processing fails
        """
        try:
            # Get and validate request data
            data = self.get_json_body()
            logger.info(f"[Telemetry] Received data: {data}")
            # Convert to CloudWatch format
            metrics = self.serialize_to_cloudwatch_format(data)
            logger.info(f"[Telemetry] Formatted metrics: {metrics}")

            # Ensure log directory exists
            log_path = '/var/log/studio/sagemaker_ext'
            os.makedirs(log_path, exist_ok=True)

            # Write formatted metrics to log file
            log_file = os.path.join(log_path, 'business_telemetry.log')
            logger.info(f"[Telemetry] Writing to file: {log_file}")
            with open(log_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')

            logger.info("[Telemetry] Successfully wrote metrics to file")
            self.finish({"status": "success"})

        except Exception as e:
            logger.exception("Failed to process telemetry data:", e)
            self.set_status(500)
            self.finish({"error": str(e)})
