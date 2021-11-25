import logging
import platform
import uuid
from typing import Dict

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.semconv.resource import ResourceAttributes
from requests.sessions import session

from metadata.__version__ import OPENMETADATA_VERSION

logger = logging.getLogger(__name__)


class OpenMetadataTelemetry:
    """
    Open Telemetry tracing.
    """

    ENDPOINT = "http://192.168.1.8:14268/api/traces"
    __send = True

    def __init__(
        self,
        send_anonymous_usage_stats: bool = True,
        user_cookie_id: str = str(uuid.uuid4()),
        local_debug_mode: bool = False,
    ):
        self.__send = send_anonymous_usage_stats
        self.__user_cookie_id = user_cookie_id
        self.__local_debug_mode = local_debug_mode
        if self.__send:
            logger.info("Sending usage telemetry.")
            self.__setup()
        else:
            logger.info("Skipping usage telemetry.")

    def __setup(self):
        provider = TracerProvider(
            resource=Resource.create(
                {
                    "os.architecture": platform.architecture(),
                    "python.version": platform.python_version(),
                    "python.implementation": platform.python_implementation(),
                    ResourceAttributes.OS_TYPE: platform.system(),
                    ResourceAttributes.OS_VERSION: platform.version(),
                    "platform": platform.platform(),
                    ResourceAttributes.SERVICE_VERSION: OPENMETADATA_VERSION,
                    ResourceAttributes.SERVICE_NAME: "openmetadata",
                    ResourceAttributes.SERVICE_NAMESPACE: "ingestion",
                }
            )
        )
        console_span_processor = BatchSpanProcessor(ConsoleSpanExporter())

        if self.__local_debug_mode or logger.getEffectiveLevel() == logging.DEBUG:
            provider.add_span_processor(console_span_processor)

        if not self.__local_debug_mode:
            otlp_exporter = OTLPSpanExporter(endpoint=self.ENDPOINT)
            # create a JaegerExporter
            jaeger_exporter = JaegerExporter(
                # configure agent
                agent_host_name="192.168.1.8",
                agent_port=6831,
                # optional: configure also collector
                # collector_endpoint='http://localhost:14268/api/traces?format=jaeger.thrift',
                # username=xxxx, # optional
                # password=xxxx, # optional
                # max_tag_value_length=None # optional
            )
            otlp_processor = BatchSpanProcessor(jaeger_exporter)
            provider.add_span_processor(otlp_processor)

        trace.set_tracer_provider(provider)

    def set_attribute(self, key: str, value: str) -> None:
        if self.__send:
            current_span = trace.get_current_span()
            current_span.set_attribute(key, value)

    @property
    def user_cookie_id(self) -> str:
        return self.__user_cookie_id


openmetadata_telemetry = OpenMetadataTelemetry()
