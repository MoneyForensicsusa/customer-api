from os import getenv

from azure.monitor.opentelemetry import configure_azure_monitor


def setup_monitoring():
    connection_string = getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        return

    configure_azure_monitor(
        connection_string=connection_string
    )