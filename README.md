# solis-sensor
HomeAssistant sensor for Solis portal platform V2 (m.ginlong.com). It logs in to the platform and exposes the data retrieved as sensors.

> Platform V2 is used by Ginlong and MyEvolveCloud and seem to be supporting different PV brands. I've only tested it in context of Solis with the Ginlong platform. Let me know if it works with for other inverter types as well.

## Manual installation

Create a directory called `solis` in the `<config directory>/custom_components/` directory on your Home Assistant instance.
Install this component by copying the files in [`/custom_components/solis/`]

"https://raw.githubusercontent.com/hultenvp/solis-sensor/master/custom_components/solis/__init__.py",
"https://raw.githubusercontent.com/hultenvp/solis-sensor/master/custom_components/solis/manifest.json"
"https://raw.githubusercontent.com/hultenvp/solis-sensor/master/custom_components/solis/sensor.py",
"https://raw.githubusercontent.com/hultenvp/solis-sensor/master/custom_components/solis/platform2_portal.py"

This is how your custom_components directory should be:
```bash
custom_components
├── solis
│   ├── __init__.py
│   ├── manifest.json
│   ├── platform2_portal.py
│   └── sensor.py
```

## Configuration example

To enable this sensor, add the following lines to your configuration.yaml file:

``` YAML
sensor:
  - platform: solis
    name: "My Solis Inverter"
    portal_domain: "m.ginlong.com"
    portal_username: "my_portal_username"
    portal_password: "my_portal_password"
    portal_plant_id: "plantId goes here"
    portal_inverter_serial: "Serial goes here"
    sensors:
      actualpower:
      energytoday:
      status:
      temperature:
      dcinputvoltagepv1:
      dcinputcurrentpv1:
      acoutputvoltage1:
      acoutputcurrent1:
      energylastmonth:
      energythismonth:
      energythisyear:
      energytotal:
```

Configuration variables:

* **name** (Optional): Let you overwrite the name of the device in the frontend. *Default value: Solis*
* **portal_domain** (Optional): Portal domain name *Default value: m.ginlong.com*.
* **portal_username** (Required): Username of your portal account.
* **portal_password** (Required): Password of the portal account. 
> Note: The integration uses https to communicate with the portal, but the username and password are sent over in plain text!
* **portal_plant_id** (Required): PlantId on the platform the inverter belongs to, log into the portal to find the pland ID under tab "plants".
> Dutch: Tab installatie: Installatie ID. 
* **inverter_serial** (Required): Serial # of the inverter itself, not the logger! Can be found under tab "devices" 
* **sensors** (Required): List of values which will be presented as sensors:
  * *actualpower*: Actual power being produced
  * *energytoday*: Total energy produced today.
> Note: This value is not necessarily zeroed at midnight but at the moment the portal receives first value from the inverter again after midnight (in my case at sunrise when the inverter switches on. May behave differently with different inverter and/or logger models)
  * *status*: Represents portal status. Online if portal is reachable, offline if portal is unreachable
  * *temperature*: Temperature of the inverter
  * *dcinputvoltagepv1*: String 1 DC voltage (0 if not present)
  * *dcinputvoltagepv2*: String 2 DC voltage (0 if not present)
  * *dcinputvoltagepv3*: String 3 DC voltage (0 if not present)
  * *dcinputvoltagepv4*: String 4 DC voltage (0 if not present)
  * *dcinputcurrentpv1*: String 1 DC current (0 if not present)
  * *dcinputcurrentpv2*: String 2 DC current (0 if not present)
  * *dcinputcurrentpv3*: String 3 DC current (0 if not present)
  * *dcinputcurrentpv4*: String 4 DC current (0 if not present)
  * *acoutputvoltage1* : Phase 1 AC voltage (0 if not present)
  * *acoutputvoltage2* : Phase 2 AC voltage (0 if not present)
  * *acoutputvoltage3* : Phase 3 AC voltage (0 if not present)
  * *acoutputcurrent1*: Phase 1 AC current (0 if not present)
  * *acoutputcurrent2*: Phase 2 AC current (0 if not present)
  * *acoutputcurrent3*: Phase 3 AC current (0 if not present)
  * *energylastmonth*: Total energy produced last month 
  * *energythismonth*: Total energy produced in current month
  * *energythisyear*: Total energy produced this year
  * *energytotal*: Total energy produced in the lifetime of the inverter

