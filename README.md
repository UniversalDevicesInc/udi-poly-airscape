# Airscape NodeServer

This is a Polyglot V2 Nodeserver for the ISY 994i to control [Airscape Whold House Fans](https://airscapefans.com/) using the [Gen 2 Controls API](https://blog.airscapefans.com/archives/gen-2-controls-api).  If you don't already own one of these awesome fans, you can not purchase the Gen 2 controller online, you have to call them.

## Installation

- Download from the Nodeservers -> Nodeserver Store
- Install from the Nodeservers -> AddNode Server
- Add the info for your fan in the NodeServer configuration page

## Requirements

- ISY Firmeware running the latest 5.x Firmware
- A machine running the [Polyglot V2](https://github.com/UniversalDevicesInc/polyglot-v2/blob/master/README.md)

## Issues

- Currently 'Set Speed' doesn't work, only 'Speed Up' and 'Speeed Down'
- When Speed Up/Speed Down are pressed, and the command is succesfully passed to the fan, the nodeserver assumes the speed is set.  In the future it will pull back the status immediatly from the fan, but this isn't simple because the fan doesn't go from 0 -> 1 right away if you have doors it waits for the doors to open enough before the fan speed changes.  If a shortPoll interval queries the fan before it goes from 0 -> 1 then it will go back to zero, but the next query will update it again.
- Need to monitor doormotion param and query in a tighter loop until it's done.

## Release Notes

- 2.0.0:
  - Initial Release
