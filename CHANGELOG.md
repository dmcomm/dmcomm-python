
## Unreleased
### Added
- Version check over serial
- More informative messages about iC decoding errors
### Changed
- Moved recommended `prong_in` on Pi Pico from GP26 to GP22
- Fixed iC escape sequence where `0x7D` is encoded as `0x7D, 0x5D`.
### Removed
- `realtime` module and example - moved to WiFiCom and has since been updated

## 0.3.0 - 2023-02-12
- First release
