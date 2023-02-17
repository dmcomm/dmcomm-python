
## Unreleased
### Added
- Version check over serial
- More informative messages about iC decoding errors
### Changed
- Changed recommended `prong_in` on Pi Pico from GP26 to GP22
- Moved `ic_encoding` module to `protocol` subpackage
- Fixed iC escape sequence where `0x7D` is encoded as `0x7D, 0x5D`
- Ensured prong weak pull and input logic level are updated when changing prong type
- Implemented prong `invert_bit_read` to give correct results for Xros Mini
- Relaxed "V" bit timing to account for D3USv1
### Removed
- `realtime` module and example - moved to WiFiCom and has since been updated

## 0.3.0 - 2023-02-12
- First release
