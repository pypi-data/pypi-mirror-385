from collections.abc import Callable, Collection, Iterable, Sequence
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    Optional,
    Union,
    cast,
    overload,
)

from aiokafka import ConsumerRecord
from aiokafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from typing_extensions import deprecated, override

from faststream._internal.broker.registrator import Registrator
from faststream._internal.constants import EMPTY
from faststream.exceptions import SetupError
from faststream.kafka.configs import KafkaBrokerConfig
from faststream.kafka.publisher.factory import create_publisher
from faststream.kafka.subscriber.factory import create_subscriber
from faststream.middlewares import AckPolicy

if TYPE_CHECKING:
    from aiokafka import TopicPartition
    from aiokafka.abc import ConsumerRebalanceListener
    from aiokafka.coordinator.assignors.abstract import AbstractPartitionAssignor
    from fast_depends.dependencies import Dependant

    from faststream._internal.types import (
        BrokerMiddleware,
        CustomCallable,
        PublisherMiddleware,
        SubscriberMiddleware,
    )
    from faststream.kafka.publisher.usecase import (
        BatchPublisher,
        DefaultPublisher,
    )
    from faststream.kafka.subscriber.usecase import (
        BatchSubscriber,
        ConcurrentBetweenPartitionsSubscriber,
        ConcurrentDefaultSubscriber,
        DefaultSubscriber,
    )


class KafkaRegistrator(
    Registrator[
        ConsumerRecord | tuple[ConsumerRecord, ...],
        KafkaBrokerConfig,
    ],
):
    """Includable to KafkaBroker router."""

    @overload  # type: ignore[override]
    def subscriber(
        self,
        *topics: str,
        batch: Literal[False] = False,
        group_id: str | None = None,
        key_deserializer: Callable[[bytes], Any] | None = None,
        value_deserializer: Callable[[bytes], Any] | None = None,
        fetch_max_bytes: int = 50 * 1024 * 1024,
        fetch_min_bytes: int = 1,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal["latest", "earliest", "none"] = "latest",
        auto_commit: Annotated[
            bool,
            deprecated(
                "This option is deprecated and will be removed in 0.7.0 release. "
                "Please, use `ack_policy=AckPolicy.ACK_FIRST` instead."
            ),
        ] = EMPTY,
        auto_commit_interval_ms: int = 5 * 1000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence["AbstractPartitionAssignor"] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 5 * 60 * 1000,
        rebalance_timeout_ms: int | None = None,
        session_timeout_ms: int = 10 * 1000,
        heartbeat_interval_ms: int = 3 * 1000,
        consumer_timeout_ms: int = 200,
        max_poll_records: int | None = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted", "read_committed"
        ] = "read_uncommitted",
        batch_timeout_ms: int = 200,
        max_records: int | None = None,
        listener: Optional["ConsumerRebalanceListener"] = None,
        pattern: str | None = None,
        partitions: Collection["TopicPartition"] = (),
        # broker args
        persistent: bool = True,
        dependencies: Iterable["Dependant"] = (),
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
        middlewares: Annotated[
            Sequence["SubscriberMiddleware[Any]"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        no_ack: Annotated[
            bool,
            deprecated(
                "This option was deprecated in 0.6.0 to prior to **ack_policy=AckPolicy.MANUAL**. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = EMPTY,
        max_workers: None = None,
        ack_policy: AckPolicy = EMPTY,
        no_reply: bool = False,
        # Specification args
        title: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
    ) -> "DefaultSubscriber": ...

    @overload
    def subscriber(
        self,
        *topics: str,
        batch: Literal[True] = ...,
        group_id: str | None = None,
        key_deserializer: Callable[[bytes], Any] | None = None,
        value_deserializer: Callable[[bytes], Any] | None = None,
        fetch_max_bytes: int = 50 * 1024 * 1024,
        fetch_min_bytes: int = 1,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal["latest", "earliest", "none"] = "latest",
        auto_commit: Annotated[
            bool,
            deprecated(
                "This option is deprecated and will be removed in 0.7.0 release. "
                "Please, use `ack_policy=AckPolicy.ACK_FIRST` instead."
            ),
        ] = EMPTY,
        auto_commit_interval_ms: int = 5 * 1000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence["AbstractPartitionAssignor"] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 5 * 60 * 1000,
        rebalance_timeout_ms: int | None = None,
        session_timeout_ms: int = 10 * 1000,
        heartbeat_interval_ms: int = 3 * 1000,
        consumer_timeout_ms: int = 200,
        max_poll_records: int | None = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted", "read_committed"
        ] = "read_uncommitted",
        batch_timeout_ms: int = 200,
        max_records: int | None = None,
        listener: Optional["ConsumerRebalanceListener"] = None,
        pattern: str | None = None,
        partitions: Collection["TopicPartition"] = (),
        # broker args
        persistent: bool = True,
        dependencies: Iterable["Dependant"] = (),
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
        middlewares: Annotated[
            Sequence["SubscriberMiddleware[Any]"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        no_ack: Annotated[
            bool,
            deprecated(
                "This option was deprecated in 0.6.0 to prior to **ack_policy=AckPolicy.MANUAL**. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = EMPTY,
        max_workers: None = None,
        ack_policy: AckPolicy = EMPTY,
        no_reply: bool = False,
        # Specification args
        title: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
    ) -> "BatchSubscriber": ...

    @overload
    def subscriber(
        self,
        *topics: str,
        batch: Literal[False] = False,
        group_id: None = None,
        key_deserializer: Callable[[bytes], Any] | None = None,
        value_deserializer: Callable[[bytes], Any] | None = None,
        fetch_max_bytes: int = 50 * 1024 * 1024,
        fetch_min_bytes: int = 1,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal["latest", "earliest", "none"] = "latest",
        auto_commit: Annotated[
            bool,
            deprecated(
                "This option is deprecated and will be removed in 0.7.0 release. "
                "Please, use `ack_policy=AckPolicy.ACK_FIRST` instead."
            ),
        ] = EMPTY,
        auto_commit_interval_ms: int = 5 * 1000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence["AbstractPartitionAssignor"] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 5 * 60 * 1000,
        rebalance_timeout_ms: int | None = None,
        session_timeout_ms: int = 10 * 1000,
        heartbeat_interval_ms: int = 3 * 1000,
        consumer_timeout_ms: int = 200,
        max_poll_records: int | None = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted", "read_committed"
        ] = "read_uncommitted",
        batch_timeout_ms: int = 200,
        max_records: int | None = None,
        listener: Optional["ConsumerRebalanceListener"] = None,
        pattern: str | None = None,
        partitions: Collection["TopicPartition"] = (),
        # broker args
        persistent: bool = True,
        dependencies: Iterable["Dependant"] = (),
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
        middlewares: Annotated[
            Sequence["SubscriberMiddleware[Any]"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        no_ack: Annotated[
            bool,
            deprecated(
                "This option was deprecated in 0.6.0 to prior to **ack_policy=AckPolicy.MANUAL**. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = EMPTY,
        max_workers: int = ...,
        ack_policy: AckPolicy = EMPTY,
        no_reply: bool = False,
        # Specification args
        title: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
    ) -> "ConcurrentDefaultSubscriber": ...

    @overload
    def subscriber(
        self,
        *topics: str,
        batch: Literal[False] = False,
        group_id: str = ...,
        key_deserializer: Callable[[bytes], Any] | None = None,
        value_deserializer: Callable[[bytes], Any] | None = None,
        fetch_max_bytes: int = 50 * 1024 * 1024,
        fetch_min_bytes: int = 1,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal["latest", "earliest", "none"] = "latest",
        auto_commit: Annotated[
            bool,
            deprecated(
                "This option is deprecated and will be removed in 0.7.0 release. "
                "Please, use `ack_policy=AckPolicy.ACK_FIRST` instead."
            ),
        ] = EMPTY,
        auto_commit_interval_ms: int = 5 * 1000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence["AbstractPartitionAssignor"] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 5 * 60 * 1000,
        rebalance_timeout_ms: int | None = None,
        session_timeout_ms: int = 10 * 1000,
        heartbeat_interval_ms: int = 3 * 1000,
        consumer_timeout_ms: int = 200,
        max_poll_records: int | None = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted", "read_committed"
        ] = "read_uncommitted",
        batch_timeout_ms: int = 200,
        max_records: int | None = None,
        listener: Optional["ConsumerRebalanceListener"] = None,
        pattern: str | None = None,
        partitions: Collection["TopicPartition"] = (),
        # broker args
        persistent: bool = True,
        dependencies: Iterable["Dependant"] = (),
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
        middlewares: Annotated[
            Sequence["SubscriberMiddleware[Any]"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        no_ack: Annotated[
            bool,
            deprecated(
                "This option was deprecated in 0.6.0 to prior to **ack_policy=AckPolicy.MANUAL**. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = EMPTY,
        max_workers: int = ...,
        ack_policy: AckPolicy = EMPTY,
        no_reply: bool = False,
        # Specification args
        title: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
    ) -> "ConcurrentBetweenPartitionsSubscriber": ...

    @overload
    def subscriber(
        self,
        *topics: str,
        batch: bool = False,
        group_id: str | None = None,
        key_deserializer: Callable[[bytes], Any] | None = None,
        value_deserializer: Callable[[bytes], Any] | None = None,
        fetch_max_bytes: int = 50 * 1024 * 1024,
        fetch_min_bytes: int = 1,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal["latest", "earliest", "none"] = "latest",
        auto_commit: Annotated[
            bool,
            deprecated(
                "This option is deprecated and will be removed in 0.7.0 release. "
                "Please, use `ack_policy=AckPolicy.ACK_FIRST` instead."
            ),
        ] = EMPTY,
        auto_commit_interval_ms: int = 5 * 1000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence["AbstractPartitionAssignor"] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 5 * 60 * 1000,
        rebalance_timeout_ms: int | None = None,
        session_timeout_ms: int = 10 * 1000,
        heartbeat_interval_ms: int = 3 * 1000,
        consumer_timeout_ms: int = 200,
        max_poll_records: int | None = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted", "read_committed"
        ] = "read_uncommitted",
        batch_timeout_ms: int = 200,
        max_records: int | None = None,
        listener: Optional["ConsumerRebalanceListener"] = None,
        pattern: str | None = None,
        partitions: Collection["TopicPartition"] = (),
        # broker args
        persistent: bool = True,
        dependencies: Iterable["Dependant"] = (),
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
        middlewares: Annotated[
            Sequence["SubscriberMiddleware[Any]"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        no_ack: Annotated[
            bool,
            deprecated(
                "This option was deprecated in 0.6.0 to prior to **ack_policy=AckPolicy.MANUAL**. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = EMPTY,
        max_workers: int | None = None,
        ack_policy: AckPolicy = EMPTY,
        no_reply: bool = False,
        # Specification args
        title: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
    ) -> Union[
        "DefaultSubscriber",
        "BatchSubscriber",
        "ConcurrentDefaultSubscriber",
        "ConcurrentBetweenPartitionsSubscriber",
    ]: ...

    @override
    def subscriber(
        self,
        *topics: str,
        batch: bool = False,
        group_id: str | None = None,
        key_deserializer: Callable[[bytes], Any] | None = None,
        value_deserializer: Callable[[bytes], Any] | None = None,
        fetch_max_bytes: int = 50 * 1024 * 1024,
        fetch_min_bytes: int = 1,
        fetch_max_wait_ms: int = 500,
        max_partition_fetch_bytes: int = 1 * 1024 * 1024,
        auto_offset_reset: Literal["latest", "earliest", "none"] = "latest",
        auto_commit: Annotated[
            bool,
            deprecated(
                "This option is deprecated and will be removed in 0.7.0 release. "
                "Please, use `ack_policy=AckPolicy.ACK_FIRST` instead."
            ),
        ] = EMPTY,
        auto_commit_interval_ms: int = 5 * 1000,
        check_crcs: bool = True,
        partition_assignment_strategy: Sequence["AbstractPartitionAssignor"] = (
            RoundRobinPartitionAssignor,
        ),
        max_poll_interval_ms: int = 5 * 60 * 1000,
        rebalance_timeout_ms: int | None = None,
        session_timeout_ms: int = 10 * 1000,
        heartbeat_interval_ms: int = 3 * 1000,
        consumer_timeout_ms: int = 200,
        max_poll_records: int | None = None,
        exclude_internal_topics: bool = True,
        isolation_level: Literal[
            "read_uncommitted", "read_committed"
        ] = "read_uncommitted",
        batch_timeout_ms: int = 200,
        max_records: int | None = None,
        listener: Optional["ConsumerRebalanceListener"] = None,
        pattern: str | None = None,
        partitions: Collection["TopicPartition"] = (),
        # broker args
        persistent: bool = True,
        dependencies: Iterable["Dependant"] = (),
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
        middlewares: Annotated[
            Sequence["SubscriberMiddleware[Any]"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        no_ack: Annotated[
            bool,
            deprecated(
                "This option was deprecated in 0.6.0 to prior to **ack_policy=AckPolicy.MANUAL**. "
                "Scheduled to remove in 0.7.0",
            ),
        ] = EMPTY,
        max_workers: int | None = None,
        ack_policy: AckPolicy = EMPTY,
        no_reply: bool = False,
        # Specification args
        title: str | None = None,
        description: str | None = None,
        include_in_schema: bool = True,
    ) -> Union[
        "DefaultSubscriber",
        "BatchSubscriber",
        "ConcurrentDefaultSubscriber",
        "ConcurrentBetweenPartitionsSubscriber",
    ]:
        """Create a subscriber for Kafka topics.

        Args:
            *topics: Kafka topics to consume messages from.
            batch: Whether to consume messages in batches or not.
            group_id:
                Name of the consumer group to join for dynamic
                partition assignment (if enabled), and to use for fetching and
                committing offsets. If `None`, auto-partition assignment (via
                group coordinator) and offset commits are disabled.
            key_deserializer:
                Any callable that takes a raw message `bytes`
                key and returns a deserialized one.
            value_deserializer:
                Any callable that takes a raw message `bytes`
                value and returns a deserialized value.
            fetch_max_bytes:
                The maximum amount of data the server should
                return for a fetch request. This is not an absolute maximum, if
                the first message in the first non-empty partition of the fetch
                is larger than this value, the message will still be returned
                to ensure that the consumer can make progress. NOTE: consumer
                performs fetches to multiple brokers in parallel so memory
                usage will depend on the number of brokers containing
                partitions for the topic.
            fetch_min_bytes:
                Minimum amount of data the server should
                return for a fetch request, otherwise wait up to
                `fetch_max_wait_ms` for more data to accumulate.
            fetch_max_wait_ms:
                The maximum amount of time in milliseconds
                the server will block before answering the fetch request if
                there isn't sufficient data to immediately satisfy the
                requirement given by `fetch_min_bytes`.
            max_partition_fetch_bytes:
                The maximum amount of data
                per-partition the server will return. The maximum total memory
                used for a request ``= #partitions * max_partition_fetch_bytes``.
                This size must be at least as large as the maximum message size
                the server allows or else it is possible for the producer to
                send messages larger than the consumer can fetch. If that
                happens, the consumer can get stuck trying to fetch a large
                message on a certain partition.
            auto_offset_reset:
                A policy for resetting offsets on `OffsetOutOfRangeError` errors:

                * `earliest` will move to the oldest available message
                * `latest` will move to the most recent
                * `none` will raise an exception so you can handle this case
            auto_commit:
                If `True` the consumer's offset will be
                periodically committed in the background.

            auto_commit_interval_ms:
                Milliseconds between automatic
                offset commits, if `auto_commit` is `True`.
            check_crcs:
                Automatically check the CRC32 of the records
                consumed. This ensures no on-the-wire or on-disk corruption to
                the messages occurred. This check adds some overhead, so it may
                be disabled in cases seeking extreme performance.
            partition_assignment_strategy:
                List of objects to use to
                distribute partition ownership amongst consumer instances when
                group management is used. This preference is implicit in the order
                of the strategies in the list. When assignment strategy changes:
                to support a change to the assignment strategy, new versions must
                enable support both for the old assignment strategy and the new
                one. The coordinator will choose the old assignment strategy until
                all members have been updated. Then it will choose the new
                strategy.
            max_poll_interval_ms:
                Maximum allowed time between calls to
                consume messages in batches. If this interval
                is exceeded the consumer is considered failed and the group will
                rebalance in order to reassign the partitions to another consumer
                group member. If API methods block waiting for messages, that time
                does not count against this timeout.
            rebalance_timeout_ms:
                The maximum time server will wait for this
                consumer to rejoin the group in a case of rebalance. In Java client
                this behaviour is bound to `max.poll.interval.ms` configuration,
                but as ``aiokafka`` will rejoin the group in the background, we
                decouple this setting to allow finer tuning by users that use
                `ConsumerRebalanceListener` to delay rebalacing. Defaults
                to ``session_timeout_ms``
            session_timeout_ms:
                Client group session and failure detection
                timeout. The consumer sends periodic heartbeats
                (`heartbeat.interval.ms`) to indicate its liveness to the broker.
                If no hearts are received by the broker for a group member within
                the session timeout, the broker will remove the consumer from the
                group and trigger a rebalance. The allowed range is configured with
                the **broker** configuration properties
                `group.min.session.timeout.ms` and `group.max.session.timeout.ms`.
            heartbeat_interval_ms:
                The expected time in milliseconds
                between heartbeats to the consumer coordinator when using
                Kafka's group management feature. Heartbeats are used to ensure
                that the consumer's session stays active and to facilitate
                rebalancing when new consumers join or leave the group. The
                value must be set lower than `session_timeout_ms`, but typically
                should be set no higher than 1/3 of that value. It can be
                adjusted even lower to control the expected time for normal
                rebalances.
            consumer_timeout_ms:
                Maximum wait timeout for background fetching
                routine. Mostly defines how fast the system will see rebalance and
                request new data for new partitions.
            max_poll_records:
                The maximum number of records returned in a
                single call by batch consumer. Has no limit by default.
            exclude_internal_topics:
                Whether records from internal topics
                (such as offsets) should be exposed to the consumer. If set to True
                the only way to receive records from an internal topic is
                subscribing to it.
            isolation_level:
                Controls how to read messages written
                transactionally.

                * `read_committed`, batch consumer will only return
                transactional messages which have been committed.

                * `read_uncommitted` (the default), batch consumer will
                return all messages, even transactional messages which have been
                aborted.

                Non-transactional messages will be returned unconditionally in
                either mode.

                Messages will always be returned in offset order. Hence, in
                `read_committed` mode, batch consumer will only return
                messages up to the last stable offset (ALSO), which is the one less
                than the offset of the first open transaction. In particular any
                messages appearing after messages belonging to ongoing transactions
                will be withheld until the relevant transaction has been completed.
                As a result, `read_committed` consumers will not be able to read up
                to the high watermark when there are in flight transactions.
                Further, when in `read_committed` the seek_to_end method will
                return the ALSO. See method docs below.
            batch_timeout_ms:
                Milliseconds spent waiting if
                data is not available in the buffer. If 0, returns immediately
                with any records that are available currently in the buffer,
                else returns empty.
            max_records: Number of messages to consume as one batch.
            listener:
                Optionally include listener
                callback, which will be called before and after each rebalance
                operation.
                As part of group management, the consumer will keep track of
                the list of consumers that belong to a particular group and
                will trigger a rebalance operation if one of the following
                events trigger:

                * Number of partitions change for any of the subscribed topics
                * Topic is created or deleted
                * An existing member of the consumer group dies
                * A new member is added to the consumer group

                When any of these events are triggered, the provided listener
                will be invoked first to indicate that the consumer's
                assignment has been revoked, and then again when the new
                assignment has been received. Note that this listener will
                immediately override any listener set in a previous call
                to subscribe. It is guaranteed, however, that the partitions
                revoked/assigned
                through this interface are from topics subscribed in this call.
            pattern:
                Pattern to match available topics. You must provide either topics or pattern, but not both.
            partitions:  An explicit partitions list to assign.
                You can't use 'topics' and 'partitions' in the same time.
            dependencies: Dependencies list (`[Dependant(),]`) to apply to the subscriber.
            parser: Parser to map original **ConsumerRecord** object to FastStream one.
            decoder: Function to decode FastStream msg bytes body to python objects.
            middlewares: Subscriber middlewares to wrap incoming message processing.
            max_workers: Number of workers to process messages concurrently.
            no_ack: Whether to disable **FastStream** auto acknowledgement logic or not.
            ack_policy: Acknowledgement policy for the subscriber.
            no_reply: Whether to disable **FastStream** RPC and Reply To auto responses or not.
            title: Specification subscriber object title.
            description: Specification subscriber object description. " "Uses decorated docstring as default.
            include_in_schema: Whetever to include operation in Specification schema or not.
            persistent: Whether to make the subscriber persistent or not.
        """
        workers = max_workers or 1

        subscriber = create_subscriber(
            *topics,
            batch=batch,
            max_workers=workers,
            batch_timeout_ms=batch_timeout_ms,
            max_records=max_records,
            group_id=group_id,
            listener=listener,
            pattern=pattern,
            connection_args={
                "key_deserializer": key_deserializer,
                "value_deserializer": value_deserializer,
                "fetch_max_wait_ms": fetch_max_wait_ms,
                "fetch_max_bytes": fetch_max_bytes,
                "fetch_min_bytes": fetch_min_bytes,
                "max_partition_fetch_bytes": max_partition_fetch_bytes,
                "auto_offset_reset": auto_offset_reset,
                "auto_commit_interval_ms": auto_commit_interval_ms,
                "check_crcs": check_crcs,
                "partition_assignment_strategy": partition_assignment_strategy,
                "max_poll_interval_ms": max_poll_interval_ms,
                "rebalance_timeout_ms": rebalance_timeout_ms,
                "session_timeout_ms": session_timeout_ms,
                "heartbeat_interval_ms": heartbeat_interval_ms,
                "consumer_timeout_ms": consumer_timeout_ms,
                "max_poll_records": max_poll_records,
                "exclude_internal_topics": exclude_internal_topics,
                "isolation_level": isolation_level,
            },
            partitions=partitions,
            # acknowledgement args
            ack_policy=ack_policy,
            no_ack=no_ack,
            auto_commit=auto_commit,
            # subscriber args
            no_reply=no_reply,
            config=cast("KafkaBrokerConfig", self.config),
            # Specification
            title_=title,
            description_=description,
            include_in_schema=include_in_schema,
        )

        super().subscriber(subscriber, persistent=persistent)

        subscriber.add_call(
            parser_=parser,
            decoder_=decoder,
            dependencies_=dependencies,
            middlewares_=middlewares,
        )

        if batch:
            return cast("BatchSubscriber", subscriber)

        if workers > 1:
            if auto_commit:
                return cast("ConcurrentDefaultSubscriber", subscriber)
            return cast("ConcurrentBetweenPartitionsSubscriber", subscriber)
        return cast("DefaultSubscriber", subscriber)

    @overload  # type: ignore[override]
    def publisher(
        self,
        topic: str,
        *,
        key: bytes | Any | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
        reply_to: str = "",
        batch: Literal[False] = False,
        # basic args
        persistent: bool = True,
        middlewares: Annotated[
            Sequence["PublisherMiddleware"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead."
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        # Specification args
        title: str | None = None,
        description: str | None = None,
        schema: Any | None = None,
        include_in_schema: bool = True,
        autoflush: bool = False,
    ) -> "DefaultPublisher": ...

    @overload
    def publisher(
        self,
        topic: str,
        *,
        key: bytes | Any | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
        reply_to: str = "",
        batch: Literal[True] = ...,
        # basic args
        persistent: bool = True,
        middlewares: Annotated[
            Sequence["PublisherMiddleware"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead."
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        title: str | None = None,
        description: str | None = None,
        schema: Any | None = None,
        include_in_schema: bool = True,
        autoflush: bool = False,
    ) -> "BatchPublisher": ...

    @overload
    def publisher(
        self,
        topic: str,
        *,
        key: bytes | Any | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
        reply_to: str = "",
        batch: bool = False,
        # basic args
        middlewares: Annotated[
            Sequence["PublisherMiddleware"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead."
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        # Specification args
        title: str | None = None,
        description: str | None = None,
        schema: Any | None = None,
        include_in_schema: bool = True,
        autoflush: bool = False,
    ) -> Union[
        "BatchPublisher",
        "DefaultPublisher",
    ]: ...

    @override
    def publisher(
        self,
        topic: str,
        *,
        key: bytes | Any | None = None,
        partition: int | None = None,
        headers: dict[str, str] | None = None,
        reply_to: str = "",
        batch: bool = False,
        # basic args
        persistent: bool = True,
        middlewares: Annotated[
            Sequence["PublisherMiddleware"],
            deprecated(
                "This option was deprecated in 0.6.0. Use router-level middlewares instead."
                "Scheduled to remove in 0.7.0",
            ),
        ] = (),
        # Specification args
        title: str | None = None,
        description: str | None = None,
        schema: Any | None = None,
        include_in_schema: bool = True,
        autoflush: bool = False,
    ) -> Union[
        "BatchPublisher",
        "DefaultPublisher",
    ]:
        """Creates long-living and Specification-documented publisher object.

        You can use it as a handler decorator (handler should be decorated by `@broker.subscriber(...)` too) - `@broker.publisher(...)`.
        In such case publisher will publish your handler return value.

        Or you can create a publisher object to call it lately - `broker.publisher(...).publish(...)`.

        Args:
            topic: Topic where the message will be published."
            key:
                A key to associate with the message. Can be used to
                determine which partition to send the message to. If partition
                is `None` (and producer's partitioner config is left as default),
                then messages with the same key will be delivered to the same
                partition (but if key is `None`, partition is chosen randomly).
                Must be type `bytes`, or be serializable to bytes via configured
                `key_serializer`.
            partition:
                Specify a partition. If not set, the partition will be
                selected using the configured `partitioner`.
            headers:
                Message headers to store metainformation.
                **content-type** and **correlation_id** will be set automatically by framework anyway.
                Can be overridden by `publish.headers` if specified.
            reply_to: Topic name to send response.
            batch: Whether to send messages in batches or not.
            middlewares: middlewares: Publisher middlewares to wrap outgoing messages.
            title: Specification publisher object title.
            description: Specification publisher object description.
            schema:
                Specification publishing message type.
                Should be any python-native object annotation or `pydantic.BaseModel`.
            include_in_schema: Whetever to include operation in Specification schema or not.
            autoflush: Whether to flush the producer or not on every publish call.
            persistent: Whether to make the publisher persistent or not.
        """
        publisher = create_publisher(
            autoflush=autoflush,
            # batch flag
            batch=batch,
            # default args
            key=key,
            # both args
            topic=topic,
            partition=partition,
            headers=headers,
            reply_to=reply_to,
            # publisher-specific
            config=cast("KafkaBrokerConfig", self.config),
            middlewares=middlewares,
            # Specification
            title_=title,
            description_=description,
            schema_=schema,
            include_in_schema=include_in_schema,
        )

        super().publisher(publisher, persistent=persistent)

        if batch:
            return cast("BatchPublisher", publisher)
        return cast("DefaultPublisher", publisher)

    @override
    def include_router(
        self,
        router: "KafkaRegistrator",  # type: ignore[override]
        *,
        prefix: str = "",
        dependencies: Iterable["Dependant"] = (),
        middlewares: Sequence["BrokerMiddleware[Any, Any]"] = (),
        include_in_schema: bool | None = None,
    ) -> None:
        if not isinstance(router, KafkaRegistrator):
            msg = (
                f"Router must be an instance of KafkaRegistrator, "
                f"got {type(router).__name__} instead"
            )
            raise SetupError(msg)

        super().include_router(
            router,
            prefix=prefix,
            dependencies=dependencies,
            middlewares=middlewares,
            include_in_schema=include_in_schema,
        )
