FROM yandex/clickhouse-server:latest

EXPOSE 9000 8123 9009

ADD users.xml /etc/clickhouse-server/users.xml

ENV CLICKHOUSE_CONFIG .custom_config.xml

ENTRYPOINT exec /usr/bin/clickhouse-server --config=${CLICKHOUSE_CONFIG}