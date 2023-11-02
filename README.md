[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# SolisCloud sensor integration
HomeAssistant sensor for SolisCloud portal. 
Still questions after the readme? Read the [wiki](https://github.com/hultenvp/solis-sensor/wiki) or look at the [discussions page](https://github.com/hultenvp/solis-sensor/discussions)

## SolisCloud
>❗The SolisCloud API is known to be unstable and can fail to respond resulting in "no inverter found" issues. See [troubleshooting](#warning--known-limitations) section. Join the discussion [here](https://github.com/hultenvp/solis-sensor/discussions/71) to find out about known limitations and to ask questions.

[SolisCloud](https://www.soliscloud.com/) is the next generation Portal for Solis branded PV systems from Ginlong. 

The new portal requires a key-id, secret and username to function.
You can obtain key and secret via SolisCloud.
* Submit a [service ticket](https://solis-service.solisinverters.com/support/solutions/articles/44002212561-api-access-soliscloud) and wait till it is resolved.
* Go to https://www.soliscloud.com/#/apiManage.
* Activate API management and agree with the usage conditions.
* After activation, click on view key tot get a pop-up window asking for the verification code.
* First click on "Verification code" after which you get an image with 2 puzzle pieces, which you need to overlap each other using the slider below.
* After that, you will receive an email with the verification code you need to enter (within 60 seconds).
* Once confirmed, you get the API ID, secret and API URL

## Platform v2 (legacy, not maintained)
Platform V2 backend was used by Ginlong before being decomissioned in May 2023. The same backend API is also used for different PV inverter brand portals. The platform v2 integration logs in to the platform and exposes the data retrieved as sensors.
Keeping as legacy for:
* Solarman (home.solarman.cn)
* Sofar solar (home.solarman.cn)

> Platform V2 backend was used by Ginlong and MyEvolveCloud and the same backend is also used for different PV inverter brand portals. I've only tested it in context of Solis with the Ginlong platform. Since Ginlong now is decomissioned I have no further means to test and will not process change requests.

## HACS installation

The use of HACS is supported and is the preferred means of installing this integration.

## Manual installation

Create a directory called `solis` in the `<config directory>/custom_components/` directory on your Home Assistant instance.
Install this component by copying the files in [`/custom_components/solis/`]

This is how your custom_components directory should be:
```bash
custom_components
├── solis
│   ├── __init__.py
│   ├── config_flow.py
│   ├── const.py
│   ├── ginlong_api.py
│   ├── ginlong_base.py
│   ├── ginlong_const.py
│   ├── manifest.json
│   ├── sensor.py
│   ├── service.py
│   ├── soliscloud_api.py
│   ├── soliscloud_const.py
│   ├── strings.json
│   └── workarounds.yaml
```
Now restart your Home Assistant Instance before continuing to the next step

### :warning:  Troubleshooting
SolisCloud is in production since 2021, but still suffers from instability. This can manifest itself as issues during setup, but also as regression/instabilities after service maintenance.
Below are issues that were encountered in the past and some suggestions how to resolve/troubleshoot.

#### No inverters found
Repeated "No inverters found" errors that do not recover automatically within a few hours sometimes block a successful configuration. Check the following:
* Check if the plant ID is present on SolisCloud. If missing then change the name of the installation by choosing "change information" on the top right of the overview page. After that a plantid is generated.
* Try creating a new API key

#### HTTP 408 Error
Not a real limitation, but a feature of the API. It caused by differences of more than 15 minutes between your local time and server time. This can happen when you run HA in a VM. ***Update your local time.***

#### Server timeouts
Just wait, they'll pass. Sometimes minutes, sometimes longer. This can be frustrating however if it happens during configuration.

#### The Chinese error message that translates into "Abnormal data"
Make sure debug is ON and make confirm you get an error messsage with Chinese text: [custom_components.solis.soliscloud_api] {'Success': True, 'Message': 'OK', 'StatusCode': 200, 'Content': {'success': True, 'code': '1', 'msg': '数据异常 请联系管理员', 'data': None}}. 
  * Alternatively copy all files from the [/test folder](https://github.com/hultenvp/solis-sensor/tree/master/test) to a local machine and make sure you have python 3 installed. Edit apitest_async.py, add your key/secret and run the test app with ```python apitest_async.py```. This test will call most API endpoints and return if the call was successful or not. You'll get the same Chinese error message if you have the "Abnormal data" problem.

Users have reported the following options as possible solutions:
* File a ticket with Solis, to solve the issue. Be prepared to wait. Can take weeks
* Deactivating (disable) the API administration in soliscloud.com and reactivating the API

***Results may vary. Do not create new tickets for this issue, it is a server error and Solis servicedesk needs to fix it for you!***

## Configuration

The integration can be configured via the UI.
* Go to Settings -> Devices and Services -> Click Add integration and select "Solis"
* Select the right platform and platform URL to use and click "Submit"
* If you add multiple configurations, make sure all of them have a unique name.

<img width="301" alt="image" src="https://user-images.githubusercontent.com/61835400/200194739-68444b7f-7144-4d84-abd0-2ac3bb82ecda.png">


**Soliscloud**            
* Provide username, key id, secret and station id. If you want to add multiple plants just repeat "add integration" for each plant.
* To get StationId: 
  1. Log in to [SolisCloud](https://www.soliscloud.com/)
  2. In the Plant Overview tab, under the Plant Name column, Click on your actual plant name, per the screenshot below:
  <img width="301" alt="image" src="https://github.com/hultenvp/solis-sensor/blob/master/image/soliscloud_mainpage.png">
  
  3. Copy the 19-digit number from the URL: https://www.soliscloud.com/#/station/stationdetail_1?id=XXXXXXXXXXXXXXXXXXX and paste it in the station ID field:
  <img width="301" alt="image" src="https://github.com/hultenvp/solis-sensor/blob/master/image/soliscloud_stationdetail.png">

If the plant id in the overview page (https://soliscloud.com/#/station/stationdetail_1?id=xxxxxxxxxxx) is empty then you will get "no inverter found errors. Change the name of the installation by choosing "change information" on the top right of the overview page. After that a plantid is generated.

**Ginlong platform v2 (deprecated, left in for legacy support)**   
* Provide username, password and plant id. If you want to add multiple plants just repeat "add integration" for each plant.

# Energy dashboard
The Solis integration now supports the energy dashboard introduced in Release 2021.8. 
> Note: This integration requires Home Assistant version 2021.9 or higher

![dashboard integration](./image/energy_dashboard_integration.GIF)
![energy production](./image/solar_production_energy_dashboard.GIF)

# Thanks
Big thanks & kudo's to [@LucidityCrash](https://github.com/LucidityCrash) for all the work on getting the SolisCloud support working!
