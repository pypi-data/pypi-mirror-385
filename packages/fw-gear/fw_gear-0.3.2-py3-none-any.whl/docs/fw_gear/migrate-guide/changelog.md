# Changelog

## v 0.3.2

**Changed/Modified**:

* Addressed potential OS command injection vulnerability in
  `utils_helpers.py` (Bandit B603, CWE-78).
* Allow container type to be `Analysis` when updating metadata.

## v 0.3.1

**Changed/Modified**:

* Made `psutil` an optional dependency under the `monitoring` extra
  group to allow users to install it only when needed for system resource tracking.

## v 0.3.0

**Changed/Modified**:

* Several submodules have been restructured and migrated from
  `flywheel_gear_toolkit` to `fw_gear`,
  bringing significant changes to the
  package architecture.
  These updates may require adjustments to imports and dependencies:
  * **`fw_gear/metadata/MetadataEncoder`**
    → relocated from `flywheel_gear_toolkit/utils/MetadataEncoder`
  * **`fw_gear/utils/archive/zip_manager.py`**
    → extracted from `flywheel_gear_toolkit/utils/zip_tools.py`
    * The following methods have been moved:
      * `unzip_archive`
      * `zip_output`
      * `zip_info`
      * `get_config_from_zip`
  * **`fw_gear/utils/licenses/freesurfer.py`**
    → transitioned from `flywheel_gear_toolkit/licenses/freesurfer.py`
  * **`fw_gear/utils/wrapper/command.py`**
    → derived from `flywheel_gear_toolkit/interfaces/command_line.py`
  * **`fw_gear/utils/wrapper/nipype.py`**
    → migrated from `flywheel_gear_toolkit/interfaces/nipype.py`
  * **`fw_gear/utils/wrapper/hpc`** → reorganized from `flywheel_gear_toolkit/hpc`
  * **`fw_gear/utils/contextutils.py`** → compiled from multiple sources:
    * Extracted from `flywheel_gear_toolkit/utils/decorators.py`:
      * `report_open_fds`
      * `report_usage_stats`
    * Relocated from `flywheel_gear_toolkit/utils/__init__.py`:
      * `sdk_post_retry_handler`
      * `sdk_delete_404_handler`
    * This module now serves as a centralized repository for decorator utilities.
  * **`fw_gear/utils/sdk_helpers.py`**
    → consolidated from `flywheel_gear_toolkit/utils/__init__.py`
    * Provides enhanced support for Flywheel SDK operations:
      * `get_container_from_ref`
      * `get_parent`
      * `setup_gear_run`
  * **`fw_gear/utils/utils.py`**
    → reorganized from `flywheel_gear_toolkit/interfaces/utils/__init__.py`
    * Contains a set of general-purpose utility functions:
      * `sanitize_label` (originated from `fw-meta`)
      * `_convert_nan`
      * `convert_nan_in_dict`
      * `deep_merge`
      * `trim`
      * `trim_lists`
      * `install_requirements`

* Several changes have been made to `GearToolkitContext`, including renaming it to
  `GearContext`
  and restructuring its implementation.
These updates require modifications
to import paths and method calls.
The setup and handling `GearToolkitContext`
have also been refined
to improve maintainability
and align with the new `fw_gear` structure.
  * **`GearToolkitContext`** has been
  renamed to **`GearContext`**, requiring all
  instances and import paths
  to be updated accordingly.
  * The handling of configuration settings
  has been enhanced by introducing
  a dedicated **`Config`** class,
  replacing the previous dictionary-based
  approach for managing `config.json`.
  * The following methods,
  previously located in `GearToolkitContext`,
  have been relocated to the `Config` class
  and must now be accessed
  via `gear_context.config.<method>`:
    * `get_input()`
    * `get_input_path()`
    * `get_input_filename()`
    * `get_input_file_object()`
    * `get_input_file_object_value()`
    * `get_destination_container()`
    * `get_destination_parent()`
    * `open_input()`

* The `Metadata` class has been updated
to enforce stricter validation
and improve metadata integrity handling.
  * `update_container()` and
  `update_file_metadata()` now
  enforce stricter validation rules,
  allowing only recognized Flywheel
  container types.
  * The `clean()` method has been improved
  to include metadata size validation,
  issuing warnings when metadata
  exceeds **16MB**.
  * A new method, `add_qc_result_to_analysis()`,
  enables the attachment of QC results
  directly to the **analysis**
  container, facilitating better metadata tracking.

**Enhancements**:

* `get_client()` has been updated
to raise a `GearContextError` when the
Flywheel SDK is unavailable or the
API key is invalid, ensuring robust
error handling and enhanced
debugging capabilities.
* The `is_fw_context()` method
has been introduced in `GearContext`
to explicitly verify if the execution
is occurring within a Flywheel
Gear environment.
* The `setup_gear_run()` function, now
available under `fw_gear.utils.sdk_helpers`,
streamlines the initialization process
for executing a gear with correctly
provisioned inputs and configurations.

**Removals**:

* Removed `download_project_bids()` and `download_session_bids()`
from `GearToolkitContext`.
* The `tempdir` feature has been
removed from `GearContext` to optimize temporary file handling.
* The `datatypes` submodule
from `flywheel_gear_toolkit.utils`
has been deprecated and removed.
* The `curator`, `reporters`, and `walker`
submodules have been extracted
from `flywheel_gear_toolkit.utils`
and are now maintained
as a separate package, `fw-curation`,
improving modularity and maintainability.
