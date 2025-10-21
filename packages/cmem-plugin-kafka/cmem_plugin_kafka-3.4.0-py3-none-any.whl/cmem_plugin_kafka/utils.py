"""Kafka utils modules"""

import json
import re
from collections.abc import Iterator
from typing import Any
from urllib.parse import urlparse

import confluent_kafka
from cmem.cmempy.config import get_cmem_base_uri
from cmem.cmempy.workspace.projects.resources.resource import get_resource_response
from cmem.cmempy.workspace.search import list_items
from cmem.cmempy.workspace.tasks import get_task
from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
    PluginContext,
    UserContext,
)
from cmem_plugin_base.dataintegration.plugins import PluginLogger
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from cmem_plugin_base.dataintegration.utils import (
    setup_cmempy_user_access,
    split_task_id,
)
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from confluent_kafka.admin import AdminClient, ClusterMetadata, TopicMetadata
from defusedxml import ElementTree
from requests import Response

from cmem_plugin_kafka.constants import KAFKA_RETRY_COUNT, KAFKA_TIMEOUT


class KafkaMessage:
    """A class used to represent/hold a Kafka Message key and value

    ...

    Attributes
    ----------
    key : str
        Kafka message key
    value : str
        Kafka message payload

    """

    def __init__(  # noqa: PLR0913
        self,
        key: str | None = None,
        headers: dict | None = None,
        value: str | None = None,
        offset: int | None = None,
        timestamp: int | None = None,
        tombstone: bool = False,
    ):
        self.value: str = value if value else ""
        self.key: str | None = key
        self.headers: dict | None = headers
        self.offset = offset
        self.timestamp = timestamp
        self.tombstone: bool = tombstone


class KafkaProducer:
    """Kafka producer wrapper over confluent producer"""

    def __init__(self, config: dict, topic: str):
        """Create Producer instance"""
        self._producer = Producer(config)
        self._topic = topic
        self._no_of_success_messages: int = 0
        self.compression_type = config.get("compression.type", "none")

    def process(self, message: KafkaMessage) -> None:
        """Produce message to topic."""
        headers = message.headers if message.headers else {}
        value = None
        if message.tombstone:
            value = None
        elif message.value:
            value = message.value.encode("utf-8")

        self._producer.produce(
            self._topic,
            value=value,
            key=message.key,
            headers=headers,
            on_delivery=self.on_delivery,
        )

    def on_delivery(self, err: confluent_kafka.KafkaError, msg: confluent_kafka.Message) -> None:
        """Execute after a message is delivered to the Kafka broker."""
        _ = msg
        if err:
            raise KafkaException(err)
        self._no_of_success_messages += 1

    def poll(self, timeout: int) -> None:
        """Poll the producer for events and calls the corresponding callbacks"""
        self._producer.poll(timeout)

    def flush(self, timeout: int = KAFKA_TIMEOUT) -> None:
        """Wait for all messages in the Producer queue to be delivered."""
        prev = 0
        while True:
            messages_in_queue = self._producer.flush(timeout=timeout)
            if prev == messages_in_queue:
                break
            prev = messages_in_queue

    def get_success_messages_count(self) -> int:
        """Return count of the successful messages"""
        return self._no_of_success_messages


class KafkaConsumer:
    """Kafka consumer wrapper over confluent consumer"""

    def __init__(
        self,
        config: dict,
        commit_offset: bool,
        topic: str,
        log: PluginLogger,
        context: ExecutionContext,
    ):
        """Create consumer instance"""
        self._consumer = Consumer(config)
        self._commit_offset = commit_offset
        self._context = context
        self._topic = topic
        self._log = log
        self._no_of_success_messages = 0
        self._first_message: KafkaMessage | None = None
        self.fetch_limit = -1

    def get_success_messages_count(self) -> int:
        """Return count of the successful messages"""
        return self._no_of_success_messages

    def commit(self) -> None:
        """Commit the latest offset"""
        if self._commit_offset:
            self._consumer.commit()

    def subscribe(self) -> None:
        """Subscribe to a topic to consume messages"""
        self._consumer.subscribe(topics=[self._topic])

    def get_first_message(self) -> KafkaMessage | None:
        """Get the first message from kafka subscribed topic"""
        if self._first_message:
            return self._first_message
        count = 0
        while True:
            msg = self._consumer.poll(timeout=KAFKA_TIMEOUT)
            count += 1
            if msg or count > KAFKA_RETRY_COUNT:
                break

        if msg is None:
            self._log.info("get_first_message: Messages are empty")
        elif msg.error():
            self._log.error(f"Consumer poll Error:{msg.error()}")
            raise KafkaException(msg.error())
        else:
            self._first_message = KafkaMessage(
                key=msg.key().decode("utf-8") if msg.key() else "",
                headers=msg.headers(),
                value=msg.value().decode("utf-8"),
                offset=msg.offset(),
                timestamp=msg.timestamp()[1],
            )
        return self._first_message

    def poll(self) -> Iterator[KafkaMessage]:
        """Poll the consumer for events and calls the corresponding callbacks"""
        while True:
            if 0 <= self.fetch_limit == self._no_of_success_messages:
                self._log.info("Message fetch fetch_limit reached")
                break

            msg = self._consumer.poll(timeout=KAFKA_TIMEOUT)
            if msg is None:
                self._log.info("Messages are empty")
                break
            if msg.error():
                self._log.error(f"Consumer poll Error:{msg.error()}")
                raise KafkaException(msg.error())

            self._no_of_success_messages += 1

            kafka_message = KafkaMessage(
                key=msg.key().decode("utf-8") if msg.key() else "",
                headers=msg.headers(),
                value=msg.value().decode("utf-8"),
                offset=msg.offset(),
                timestamp=msg.timestamp()[1],
            )

            if not self._first_message:
                self._first_message = kafka_message
            if not self._no_of_success_messages % 10:
                self._context.report.update(
                    ExecutionReport(
                        entity_count=self._no_of_success_messages,
                        operation="read",
                        operation_desc="messages received",
                    )
                )
            yield kafka_message

    def close(self) -> None:
        """Close the consumer once all messages were received."""
        self._consumer.close()


def get_default_client_id(project_id: str, task_id: str) -> str:
    """Return dns:projectId:taskId when client id is empty"""
    base_url = get_cmem_base_uri()
    dns = urlparse(base_url).netloc
    return f"{dns}:{project_id}:{task_id}"


def validate_kafka_config(config: dict[str, Any], topic: str, log: PluginLogger) -> None:
    """Validate kafka configuration"""
    admin_client = AdminClient(config)
    cluster_metadata: ClusterMetadata = admin_client.list_topics(topic=topic, timeout=KAFKA_TIMEOUT)

    topic_meta: TopicMetadata = cluster_metadata.topics[topic]
    kafka_error: KafkaError = topic_meta.error

    if kafka_error and kafka_error.code() == KafkaError.LEADER_NOT_AVAILABLE:
        raise ValueError(
            "The topic you configured, was just created. Save again if this ok for you."
            " Otherwise, change the topic name."
        )
    if kafka_error:
        raise kafka_error
    log.info("Connection details are valid")


def get_resource_from_dataset(dataset_id: str, context: UserContext) -> tuple[Response, dict]:
    """Get resource from dataset"""
    project_id, task_id = split_task_id(dataset_id)
    task_meta_data = get_task_metadata(project_id, task_id, context)
    resource_name = str(task_meta_data["data"]["parameters"]["file"]["value"])

    return get_resource_response(project_id, resource_name), task_meta_data


def get_task_metadata(project: str, task: str, context: UserContext) -> dict:
    """Get metadata information of a task"""
    setup_cmempy_user_access(context=context)
    return dict(get_task(project=project, task=task))


def get_message_with_xml_wrapper(message: KafkaMessage) -> str:
    """Wrap kafka message around Message tags"""
    is_xml(message.value)
    # strip xml metadata
    regex_pattern = "<\\?xml.*\\?>"
    msg_with_wrapper = f'<Message key="{message.key}">'
    msg_with_wrapper += re.sub(regex_pattern, "", message.value)
    msg_with_wrapper += "</Message>\n"
    return msg_with_wrapper


class BytesEncoder(json.JSONEncoder):
    """JSON Bytes Encoder"""

    def default(self, o: str | bytes) -> str:
        """Return the serializable object of o"""
        if isinstance(o, bytes):
            return o.decode("utf-8")
        return json.JSONEncoder.default(self, o)  # type: ignore[no-any-return]


def get_message_with_json_wrapper(message: KafkaMessage) -> str:
    """Wrap kafka message around Message tags"""
    msg_with_wrapper = {"message": {"key": message.key, "content": json.loads(message.value)}}
    if message.headers:
        msg_with_wrapper["message"]["headers"] = {
            header[0]: header[1] for header in message.headers
        }
    return json.dumps(msg_with_wrapper, cls=BytesEncoder)


def get_kafka_statistics(json_data: str) -> dict:
    """Return kafka statistics from json"""
    interested_keys = [
        "name",
        "client_id",
        "type",
        "time",
        "msg_cnt",
        "msg_size",
        "topics",
    ]
    stats = json.loads(json_data)
    return {
        key: ",".join(stats[key].keys()) if isinstance(stats[key], dict) else f"{stats[key]}"
        for key in interested_keys
    }


def is_xml(value: str) -> None:
    """Check value is xml string or not"""
    try:
        ElementTree.fromstring(value)
    except ElementTree.ParseError as exc:
        raise ValueError(f"Kafka message({value}) is not in Valid XML format") from exc


def is_json(value: str) -> bool:
    """Check value is json string or not"""
    try:
        json.loads(value)
    except json.decoder.JSONDecodeError:
        return False
    return True


class DatasetParameterType(StringParameterType):
    """Dataset parameter type."""

    allow_only_autocompleted_values: bool = True

    autocomplete_value_with_labels: bool = True

    dataset_type: str | None = None

    def __init__(self, dataset_type: str = ""):
        """Dataset parameter type."""
        self.dataset_type = dataset_type

    def label(
        self, value: str, depend_on_parameter_values: list[Any], context: PluginContext
    ) -> str | None:
        """Return the label for the given dataset."""
        _ = depend_on_parameter_values
        setup_cmempy_user_access(context.user)
        task_label = str(get_task(project=context.project_id, task=value)["metadata"]["label"])
        return f"{task_label}"

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion request. Returns all results that match ALL provided query terms."""
        _ = depend_on_parameter_values
        setup_cmempy_user_access(context.user)
        datasets = list_items(item_type="dataset", project=context.project_id)["results"]

        result = []
        dataset_types = []
        if self.dataset_type:
            dataset_types = self.dataset_type.split(",")

        for _ in datasets:
            identifier = _["id"]
            title = _["label"]
            label = f"{title} ({identifier})"
            if dataset_types and _["pluginId"] not in dataset_types:
                # Ignore datasets of other types
                continue

            result.extend(
                [
                    Autocompletion(value=identifier, label=label)
                    for term in query_terms
                    if term.lower() in label.lower()
                ]
            )
            if len(query_terms) == 0:
                # add any dataset to list if no search terms are given
                result.append(Autocompletion(value=identifier, label=label))
        result.sort(key=lambda x: x.label)
        return list(set(result))
