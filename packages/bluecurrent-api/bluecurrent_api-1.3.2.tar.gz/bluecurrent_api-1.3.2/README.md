# Blue Current Api

[![Documentation Status](https://readthedocs.com/projects/blue-current-homeassistantapi/badge/?version=latest&token=00ce4a850aedc0993b7075a8b2d5f8de98251adcdb4eada1f1fb3c02fee80039)](https://blue-current-homeassistantapi.readthedocs-hosted.com/en/latest/?badge=latest)

Python wrapper for the blue current api

The library is an asyncio-driven library that interfaces with the Websocket API provided by Blue Current. This was made for the Blue Current Home Assistant integration.

## Usage

### Requirements

- Python 3.11 or newer
- websockets

### Installation

```python
pip install bluecurrent-api
```

### Api token

Using this library requires a Blue Current api token. You can generate one in the Blue Current driver portal.

## Example

```python
from bluecurrent_api import Client
import asyncio


async def main():
    api_token = 'api_token'
    client = Client()

    # data receiver
    async def on_data(data):
        print('received: ', data)

    # validate and set token.
    await client.validate_api_token(api_token)

    # example requests
    async def on_open():
        await client.get_charge_points()
        await asyncio.sleep(10)
        await client.disconnect()

    # connect and send requests
    await client.connect(on_data, on_open)

asyncio.run(main())
```

## Implemented methods

---

<b>The methods validate_token and get_email are stand-alone and are to be used <u>before</u> connecting to the websocket with connect().</b>

<br>

#### await validate_token(api_token) -> str

- Validates the given token.

#### await get_email() -> str

- Returns the account's email.

---

#### await connect(receiver)

- Connects to the websocket.
- Calls get_charge_points and get_charge_cards when connection is established.

#### is_connected() -> bool
- Returns if the client is connected

#### await wait_for_charge_points()
- Waits until chargepoints are received.


#### get_next_reset_delta() -> TimeDelta

- Returns the timedelta to the next request limit reset (00:00 Europe/Amsterdam).

#### await disconnect()

- Stops the connection.

<br>

### Data

---

#### await get_charge_points()

- Gets the chargepoints

#### await get_charge_cards()

- Returns the users charge cards.

#### await get_status(evse_id)

- Gets the status from a chargepoint.

#### await get_settings(evse_id)

- Gets the setting states from a chargepoint.

#### await get_grid_status(evse_id)

- Gets the grid status from a chargepoint.

#### await get_user_override_currents_list()

- Returns a list with current override values set by the user and the related scheduling data.

<br>

### Settings

---

#### await set_linked_charge_cards_only(evse_id, value)

- Sets set_linked_charge_cards_only.

#### await set_plug_and_charge(evse_id, value)

- Sets set_plug_and_charge.

#### await block(evse_id, value)

- Blocks or unblocks a charge point.

<br>

### Actions

---

#### await reset(evse_id)

- Resets the chargepoint.

#### await reboot(evse_id)

- Reboots the chargepoint.

#### await start_session(evse_id card_uid)

- Starts a charge session.

#### await stop_session(evse_id)

- Stops a charge session.

#### await set_delayed_charging(evse_id, value)

- Turns smart charging profile on/off and sets the profile to delayed charging.

#### await set_delayed_charging_settings(evse_id, days, start_time, end_time)

- Sends the settings for the scheduling of the delayed charging profile.

#### await set_price_based_charging(evse_id, value)

- Turns smart charging profile on/off and sets the profile to price based charging.

#### await set_price_based_settings(evse_id, expected_departure_time, expected_kwh, minimum_kwh)

- Sends the settings for the price based charging profile.

#### await override_price_based_charging_profile(evse_id: str, value)

- Overrides the settings set up by the price based charging profile and starts charging immediately.

#### await override_delayed_charging_profile(evse_id, value)

- Overrides the timeout set by the delayed charging profile and starts charging immediately.

#### await set_user_override_current(payload)

- Schedules an override of the electricity current that chargepoints are allowed
         to use when charging.

#### await clear_user_override_current(schedule_id)

- Clears a previously set user override using the given schedule ID.

#### edit_user_override_current(schedule_id, payload)

- Lets the user edit a scheduled override of the electricity current that chargepoints
         are allowed to use when charging.

