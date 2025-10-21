# Global Notifier Service (GNS)

The global notifier service (shortened to GNS) is the component responsible for sending out kafka messages following state changes across MCM.

## User Manual
[GNS User Manual](https://www.notion.so/ml-infra/GNS-User-Manual-0ff91d24727380d89203d79046b45ad6)

## How it Works

GNS is a change data capture (CDC) messenging system which works by using a postgres replication plugin called [wal2json](https://github.com/eulerto/wal2json). This plugin runs on the postgres server, consuming, translating, and emitting json-formatted write-ahead log (WAL) messages for consumption. GNS is then responsible for reading in these wal2json messages, then translating that into the requisite kafka topics used across MCM.

## Why Change Data Capture for MCM?

We chose to use a change data capture patturn for MCM because it guarantees at-least once delivery semantics and ensures that once something is written to the database a message will be emitted. Without it (i.e. with each component sending kafka messages directly to other components) there could be conditions where something was written to the db and no message was emitted or vice versa.

## How it is Architected

GNS is set up with a set of polymorphic handlers which are bound to a slot consumer (replication slot). When GNS comes up it:

 - Detects which tables it is responsible for from the configuration. The slot it is configured for is passed via the CLI.
 - Sets up a wal2json replication slot consumer for the subset of tables it is responsible for.
 - Detects which handlers want to consume from the table we are consuming for.
 - Passes those handlers in to the slot consumer
 - Manage the replication protocol messages (keepalive, etc) and send data messages for processing by the handlers.
 - Handlers unpack the wal2json messages, translate them into the right protobuf message format, then emit them to kafka.
