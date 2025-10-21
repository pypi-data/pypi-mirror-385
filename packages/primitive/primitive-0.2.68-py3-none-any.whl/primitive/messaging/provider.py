import enum
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

import pika
from loguru import logger
from pika import credentials

from primitive.utils.actions import BaseAction
from primitive.__about__ import __version__
from ..utils.x509 import (
    are_certificate_files_present,
    create_ssl_context,
    read_certificate_common_name,
)

if TYPE_CHECKING:
    import primitive.client

EXCHANGE = "hardware"
ROUTING_KEY = "hardware"
VIRTUAL_HOST = "primitive"
CELERY_TASK_NAME = "hardware.tasks.task_receive_hardware_message"


class MESSAGE_TYPES(enum.Enum):
    CHECK_IN = "CHECK_IN"
    METRICS = "METRICS"
    SWITCH_AND_INTERFACES_INFO = "SWITCH_AND_INTERFACES_INFO"
    OWN_NETWORK_INTERFACES = "OWN_NETWORK_INTERFACES"


class MessagingProvider(BaseAction):
    def __init__(self, primitive: "primitive.client.Primitive") -> None:
        super().__init__(primitive=primitive)
        self.ready = False

        self.fingerprint = self.primitive.host_config.get("fingerprint", None)
        if not self.fingerprint:
            return
        self.token = self.primitive.host_config.get("token", None)
        if not self.token:
            return

        rabbitmq_host = "rabbitmq-cluster.primitive.tech"
        RABBITMQ_PORT = 443

        if primitive.host == "api.dev.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.dev.primitive.tech"
        elif primitive.host == "api.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.primitive.tech"
        elif primitive.host == "api.staging.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.staging.primitive.tech"
        elif primitive.host == "api.test.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.test.primitive.tech"
        elif primitive.host == "localhost:8000":
            rabbitmq_host = primitive.host.split(":")[0]
            RABBITMQ_PORT = 5671

        if not are_certificate_files_present():
            logger.warning(
                "Certificate files not present or incomplete. MessagingProvider not initialized."
            )
            return

        ssl_context = create_ssl_context()
        ssl_options = pika.SSLOptions(ssl_context)
        self.common_name = read_certificate_common_name()

        self.parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=RABBITMQ_PORT,
            virtual_host=VIRTUAL_HOST,
            ssl_options=ssl_options,
            credentials=credentials.ExternalCredentials(),
        )

        self.ready = True

    def send_message(self, message_type: MESSAGE_TYPES, message: dict[str, any]):  # type: ignore
        if not self.ready:
            logger.warning(
                "send_message: cannot send message. MessagingProvider not initialized."
            )
            return

        body = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_type": message_type.value,
            "message": message,
        }

        full_body_for_celery = [
            [],
            body,
            {"callbacks": None, "errbacks": None, "chain": None, "chord": None},
        ]
        with pika.BlockingConnection(parameters=self.parameters) as conn:
            message_uuid = str(uuid4())
            channel = conn.channel()

            headers = {
                "fingerprint": self.fingerprint,
                "version": __version__,
                "token": self.token,
                "argsrepr": "()",
                "id": message_uuid,
                "ignore_result": False,
                "kwargsrepr": str(body),
                "lang": "py",
                "replaced_task_nesting": 0,
                "retries": 0,
                "root_id": message_uuid,
                "task": CELERY_TASK_NAME,
            }

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY,
                body=json.dumps(full_body_for_celery),
                properties=pika.BasicProperties(
                    user_id=self.common_name,
                    correlation_id=message_uuid,
                    priority=0,
                    delivery_mode=2,
                    headers=headers,
                    content_encoding="utf-8",
                    content_type="application/json",
                ),
            )
