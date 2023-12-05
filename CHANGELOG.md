
## Unreleased
### Added
- High-level DigiROM API for DMOG
- Version info with "i" following the pattern decided in other DMComm variants
- Pause command with "P"
### Changed
- Results of `parse_command`:
    - "?" changed to "I"
    - new "P" for "pause"
    - removed "D"
    - `turn` now considered to exist if the first text segment ends with a digit
    - Added `signal_type = None` to `OtherCommand` for easier distinguishing from DigiROMs
    - Removed `param` from `OtherCommand`
- Copied `board_config.py` from wificom-lib v1.1.0 for easier switching between dmcomm and wificom
- Rewrote DL/FL/LT receiving to count pulse+gap duration, rather than pulses and gaps separately - improves the situation for non-Vishay TSOP4838
- Rewrote example for high-level DigiROM API
- Deinit weak pull when prongs are disabled (caused issues combined with past "disable after every transmission" behaviour, but OK now)
- Separated DMC logic - `ProngCommunicator` became `ClassicCommunicator` and `ColorCommunicator` - `ClassicCommunicator` follows program flow from before DMC was added
- IR barcodes changed from 100% duty cycle to 15/16 so that IrDA modules will allow them
### Removed
- Data serial option
- Workaround for PIO bug in CircuitPython 8.0.0 alpha versions

## 0.7.0 - 2023-05-06
### Added
- Calculation features in sequence DigiROMs:
    - Normal checksum using "++", or "++++" for DMC
    - Normal mirroring using "__", or "____" for DMC
    - Data Link ID shift using ">>"
    - Data Link checksum calculation using "+?"
### Changed
- Major reorganization of DigiROM API (but `parse_command` API is unchanged)
- Files have moved around so recommend deleting old `lib/dmcomm` folder before upgrading
- Finalized Data Link - removed "!" - bytes are reversed from "!" version, `utils/byte_reverse.py` can fix existing Data Link byte sequences in text files
- Finalized Fusion Loader - removed "!!" with no changes
### Tested with
- CircuitPython 8.0.5

## 0.6.0 - 2023-04-17
### Added
- Basic support for Digimon Color
### Changed
- Changed ending of serial output lines from "\n" to "\r\n" to match Arduino
- Fixed serial `UnicodeError`
- `boot.py` changes:
    - added Pico W button support
    - disabled status bar
    - made CIRCUITPY drive read-only by default instead of disabling
    - more informative messages (visible in `boot_out.txt`)
- Relaxed timings for Data Link and English DMOG

## 0.5.0 - 2023-02-19
### Added
- Default Pi Pico W pins in `board_config` (same as Pico except LED)
- Configurable `led_pin` in `board_config`

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
