"""
This script will read temperatures of both sensors currently connected to the DAQ6510.

The sensors are connected to:

- the hot water buffer tank
- room temperature (central heating room)

Run the script as follows:

$ py projects/generic/keithley-tempcontrol/tests/script_daq6510_central_heating.py

The data will be stored in JSON format in the file 'buffer_vat.log'.

"""

import asyncio
import json
import time

from egse.log import logger
from egse.tempcontrol.keithley.daq6510_mon import DAQMonitorClient
from egse.tempcontrol.keithley.daq6510_mon import DAQ_MON_CMD_PORT


def daq6510_mon_cv():
    with DAQMonitorClient(server_address="localhost", port=DAQ_MON_CMD_PORT) as client:
        # Get current status
        status = client.get_status()
        logger.info(f"Service status: {json.dumps(status, indent=4)}")

        # Set polling interval to 10s
        response = client.set_interval(10.0)
        logger.info(f"Set interval response: {response}")

        response = client.start_polling(channels=["101", "102"])
        logger.info(f"Start polling response: {response}")

        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("Caught keyboard interrupt, terminating...")

        response = client.stop_polling()
        logger.info(f"Stop polling response: {response}")

        client.shutdown()
        logger.info(f"DAQ6510 monitor shutdown requested.")


if __name__ == "__main__":
    daq6510_mon_cv()
