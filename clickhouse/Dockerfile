FROM yandex/clickhouse-server:latest

EXPOSE 9000 8123 9009

ADD ./users.xml /etc/clickhouse-server/users.xml
ADD ./custom_config.xml /etc/clickhouse-server/custom_config.xml

ENV CLICKHOUSE_CONFIG /etc/clickhouse-server/config.xml

ENTRYPOINT exec /usr/bin/clickhouse-server --config=${CLICKHOUSE_CONFIG}
