# IPS Controllers API Client

Python client library for the IPS Controllers pool monitoring system.

## Installation

```bash
pip install ips-api-client
```

## Usage

```python
import asyncio
from ips_api import IPSClient

async def main():
    async with IPSClient("your_email@example.com", "your_password") as client:
        # Get all controllers
        controllers = await client.get_controllers()

        for controller in controllers:
            print(f"Controller: {controller.name}")
            print(f"  pH: {controller.current_reading.ph}")
            print(f"  ORP: {controller.current_reading.orp} mV")
            print(f"  Status: {controller.status}")

            # Get detailed reading
            detail = await client.get_controller_detail(controller.controller_id)
            print(f"  pH Setpoint: {detail.ph_setpoint}")
            print(f"  pH State: {detail.ph_state}")

asyncio.run(main())
```

## Features

- Async/await support
- Automatic session management
- Support for multiple controllers
- Detailed pool chemistry readings (pH, ORP, temperature, chlorine)
- Controller status monitoring

## Data Available

- pH level
- ORP (Oxidation-Reduction Potential) in mV
- Water temperature (when available)
- Chlorine PPM (when available)
- Controller status
- Last reading timestamp
- pH setpoint and state

## License

MIT
