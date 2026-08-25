from sandbox.clickhouse import get_client

client = get_client()
print("Connected to ClickHouse:", client.server_version)
