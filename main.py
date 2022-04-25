import asyncio
import os

from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

DEBUG = os.getenv("DEBUG", False)
DEVICE = os.getenv("DEVICE", "My Device")
HOST = os.getenv("INFLUX_HOST", "https://us-central1-1.gcp.cloud2.influxdata.com") # noqa
TOKEN = os.getenv("INFLUX_TOKEN")
ORG = os.getenv("INFLUX_ORG")
BUCKET = os.getenv("INFLUX_BUCKET", "system-metrics")
INTERFACE = os.getenv("INTERFACE", "wlan0")


async def get_bytes(t, iface=INTERFACE):
    with open('/sys/class/net/' + iface + '/statistics/' + t + '_bytes', 'r') as f: # noqa
        data = f.read()
        return int(data)


async def main():
    client = InfluxDBClient(url=HOST, token=TOKEN, org=ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        # Collect stats
        tx1 = await get_bytes('tx')
        rx1 = await get_bytes('rx')

        await asyncio.sleep(1)

        tx2 = await get_bytes('tx')
        rx2 = await get_bytes('rx')

        tx_speed = round((tx2 - tx1)/1000000.0, 4)
        rx_speed = round((rx2 - rx1)/1000000.0, 4)

        if DEBUG:
            os.system('clear||cls')
            print("-- Netmon --")
            print("")
            # NET
            print("tx_speed", tx_speed)
            print("rx_speed", rx_speed)
            print("")

        # Write data to InfluxDB
        POINT = Point("system-metrics") \
            .tag("device", DEVICE) \
            .field("tx_speed", tx_speed) \
            .field("rx_speed", rx_speed) \
            .time(datetime.utcnow(), WritePrecision.NS)
        write_api.write(bucket=BUCKET, record=POINT)

if __name__ == "__main__":
    print("Netmon is running...")
    asyncio.run(main())
