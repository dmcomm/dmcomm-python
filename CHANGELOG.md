
## 0.4.0 - 2023-02-17
### Added
- Version check over serial
- More informative messages about iC decoding errors
### Changed
- Changed recommended `prong_in` on Pi Pico from GP26 to GP22
- Renamed `physical` and `protocol` attributes to `signal_type` - major breaking change to API (most API users will have been using `digirom.physical`)
- Moved `ic_encoding` module from `hardware` to `protocol` subpackage
- Fixed iC escape sequence where `0x7D` is encoded as `0x7D, 0x5D`
- Ensured prong weak pull and input logic level are updated when changing prong type
- Implemented prong `invert_bit_read` to give correct results for Xros Mini
- Relaxed "V" bit timing to account for D3USv1
- Relaxed Talis start bit timing to see if this works around the reliability issue
### Removed
- `realtime` module and example - moved to WiFiCom and has since been updated
### Tested with
- CircuitPython 8.0.2

## 0.3.0 - 2023-02-12
- First release
