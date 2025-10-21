# Release Notes

## 0.3.2

__Enhancement__:

* Updated manifest schema to require and validate config property types,
  ensuring all config properties specify a type from the allowed set: string,
  integer, number, boolean, or array.
* `fw_gear.utils.wrapper.command.exec_command`: added live streaming
  controls (`stream` + `stream_mode`)
  and optional `logfile` tee; improved env merging and safer shell handling.

__Breaking Changes__:

* Removed `stdout_msg` parameter from `fw_gear.utils.wrapper.command.exec_command`.
  This parameter previously allowed logging a custom message instead of command output
  and disabled streaming when provided.

__Maintainence__:

* Addressed potential OS command injection vulnerability when running
  external commands.

__Bug Fix__:

* Fixed issue where `GearContext` would raise a `FileNotFoundError` when
  initialized without a manifest.json file.
* Allow container type to be `Analysis` when updating metadata.
* Prevented pipe deadlocks in live streaming by merging `stderr` into `stdout`
  during streaming for `fw_gear.utils.wrapper.command.exec_command`

## 0.3.1

__Enhancement__:

* Updated `psutil` as optional dependency, allowing users to skip
  installation unless needed.
* Update gear manifest schema to include Flywheel gear classification.

## 0.3.0

__Enhancement__:

* Rollback on `update_file_metadata` to allow updating file metadata
  with file name and container_type inputs
* Added warning when `fw_path` and `local_path` is not available.
* Added missing methods from flywheel-gear-toolkit -
  `get_input_file_object` and `get_input_file_object_value`
* Improved error handling in `get_client()` — now raises `GearContextError`
  if the SDK is unavailable or the API key is invalid.
* Introduced `is_fw_context()` to explicitly check for Flywheel Gear runtime.
* Added `setup_gear_run()` to streamline gear setup and config handling.

__MAINTENANCE__:

* Major refactor: core modules migrated from `flywheel_gear_toolkit` to `fw_gear`.

* `GearToolkitContext` renamed and replaced by `GearContext`;
config handling is now managed via a new `Config` class.

* Refactored utility methods and decorators under `fw_gear/utils` structure.

* `Metadata` class now validates container types more strictly
and adds metadata size warnings (>16MB).

* New `add_qc_result_to_analysis()` method to attach QC results to analysis containers.

__DEPRECATIONS__:

* Removed `download_project_bids()` and `download_session_bids()`.

* Removed `tempdir` support from `GearContext`.

* Deprecated `datatypes`, `curator`, `reporters`, and `walker` — now moved to
`fw-curation`.
