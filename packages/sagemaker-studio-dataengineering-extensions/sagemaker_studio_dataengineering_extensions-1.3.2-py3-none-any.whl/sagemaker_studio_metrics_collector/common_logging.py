import os
import logging
import datetime
import inspect
import traceback
from functools import wraps
from tornado import web
import botocore

from aws_embedded_metrics.sinks.stdout_sink import StdoutSink, Sink
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger
from aws_embedded_metrics.logger.metrics_context import MetricsContext
from aws_embedded_metrics.environment.local_environment import LocalEnvironment

from sagemaker_studio_metrics_collector.utils.error_util import ErrorMatcher
from sagemaker_studio_metrics_collector.utils.aws_config import get_aws_account_id
from sagemaker_studio_metrics_collector.utils.app_metadata import (
    get_domain_id,
    get_user_profile_name,
    get_shared_space_name,
    get_sagemaker_image,
    get_sagemaker_environment,
)
from sagemaker_studio_metrics_collector.utils.environment_detector import (
    JupyterLabEnvironment,
)
from sagemaker_studio_metrics_collector.utils.stack_trace_filter import StackTraceFilter


DEFAULT_LOG_FILE_PATH = "/var/log/studio/sagemaker_ext"
DEFAULT_LOG_FILE_NAME = "sagemaker_extensions.log"
LOGGER_NAME = "sagemaker_metrics_collector_log"
def init_common_metrics_logger(server_log):
    try:
        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(logging.INFO)
        log_file_location = os.path.join(DEFAULT_LOG_FILE_PATH, DEFAULT_LOG_FILE_NAME)
        os.makedirs(DEFAULT_LOG_FILE_PATH, exist_ok=True)
        file_handler = logging.FileHandler(log_file_location)
        logger.addHandler(file_handler)
        logger.propagate = False
        server_log.info(f"Common metrics logger initialized at: {log_file_location}")

    except Exception as e:
        server_log.error(f"Failed to initialize common metrics logger: {str(e)}")

class LogFileSink(StdoutSink):
    def accept(self, context: MetricsContext) -> None:
        for serialized_content in self.serializer.serialize(context):
            if serialized_content:
                logging.getLogger(LOGGER_NAME).info(serialized_content)

    @staticmethod
    def name() -> str:
        return "LogFileSink"


class LogFileEnvironment(LocalEnvironment):
    def get_sink(self) -> Sink:
        return LogFileSink()


async def resolve_environment():
    return LogFileEnvironment()


def _extract_codes(excep):
    """Extract HTTP and error codes from exceptions."""
    http_code = "500"
    error_code = "InternalError"

    try:
        if isinstance(excep, web.HTTPError):
            http_code = f"{excep.status_code}"
            # we construct the log_message from boto ClientError in error_utils function, so no risk of viewing customer information
            # we always add the delimiter :
            # f"{error.response['Error']['Code']}: {error.response['Error']['Message']}",
            error_code = excep.log_message.split(":")[0]

        elif isinstance(excep, botocore.exceptions.ClientError):
            # we dont wrap all api error in web.HTTPError, so catching it here
            error_code = f"{excep.response['Error']['Code']}"
            http_code = f"{excep.response['ResponseMetadata']['HTTPStatusCode']}"

        elif isinstance(excep, botocore.exceptions.EndpointConnectionError):
            error_code = "503"
            http_code = "EndpointConnectionError"

        elif isinstance(excep, botocore.exceptions.NoCredentialsError):
            http_code = "403"
            error_code = "NoCredentials"

        else:
            http_code = "500"
            error_code = str(type(excep))

    except Exception:
        # Logging should not impact main functionality
        # silently fail indicating Internal Error
        error_code = "InternalErrorLogging"

    return http_code, error_code


def get_metric_namespace(extension_name=None):
    logger = logging.getLogger(LOGGER_NAME)
    base_namespace = "SageMakerUnifiedStudio"
    if not extension_name:
        return base_namespace
    namespace = f"{base_namespace}{extension_name.capitalize()}"
    environment = get_sagemaker_environment()
    if environment in [JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO, JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB]:
        return f"{namespace}-JupyterLab"
    return namespace

def async_with_metrics(operation, extension_name=None):
    def decorate(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = logging.getLogger(LOGGER_NAME)
            start_time = datetime.datetime.now()
            error = fault = 0
            http_code = "200"
            error_code = "Success"
            is_exception = False
            em = ErrorMatcher()

            context = MetricsContext().empty()
            metrics_logger = MetricsLogger(resolve_environment, context)
            if "metrics" in inspect.signature(func).parameters:
                kwargs["metrics"] = metrics_logger

            try:
                return await func(*args, **kwargs)
            except Exception as excep:
                http_code, error_code = _extract_codes(excep)
                is_exception = True
                # convert to Schedule Error and pass the error message, this will ensure the customers can see the exact error message
                logger.info(f"Exception in {operation}: code={error_code}, http={http_code}")
                logging.getLogger(LOGGER_NAME).info(excep)
                raise
            finally:
                if is_exception:
                    if em.is_fault(str(error_code)):
                        fault = 1
                    else:
                        error = 1
                    stack_trace = traceback.format_exc()
                    context.set_property("StackTrace", stack_trace_filter.filter(stack_trace))
                try:
                    context.namespace = get_metric_namespace(extension_name)
                    context.should_use_default_dimensions = False
                    context.put_dimensions({"Operation": operation})
                    context.set_property("AccountId", await get_aws_account_id())
                    context.set_property("UserProfileName", get_user_profile_name())
                    context.set_property("SharedSpaceName", get_shared_space_name())
                    context.set_property("DomainId", get_domain_id())
                    context.set_property("HTTPErrorCode", http_code)
                    context.set_property("BotoErrorCode", error_code)
                    context.set_property("Image", get_sagemaker_image())
                    context.put_metric("Error", error, "Count")
                    context.put_metric("Fault", fault, "Count")
                    elapsed = datetime.datetime.now() - start_time
                    context.put_metric(
                        "Latency", int(elapsed.total_seconds() * 1000), "Milliseconds"
                    )
                    await metrics_logger.flush()
                except Exception as excep:
                    # we log and silently fail for the extra information that we add
                    # and not affect any api operations
                    logging.getLogger(LOGGER_NAME).info(excep)
                    pass

        return wrapper

    return decorate
