<!-- Disable annoying code fencing rule which gets triggered on admonitions -->
<!-- markdownlint-disable MD046 MD007 MD013-->
# Gear Context

The `fw_gear.context.GearContext` is an iteration on the Flywheel SDK's `GearContext`
(`flywheel.GearContext`).

!!! note

    The `fw-gear` package is a reworked and
    enhanced version of the `flywheel_gear_toolkit`
    Python package.
    Please note that `flywheel_gear_toolkit`
    is scheduled for reaching end-of-life in 2026.

The `fw_gear.context.GearContext` class provides an
interface for performing common tasks in the lifecycle of a gear, such as:

* Accessing input files, configuration values, and manifest properties and an SDK client
* Configuring logging
* Writing to output files and output metadata (.metadata.json)

## Structure

The `GearContext` class is composed of:

* `fw_gear.config.Config` object, which represents the `config.json` within a
  gear run that holds all the gears _provided_ runtime options (inputs,
  configuration values).  See more at
  [Accessing Gear Runtime](#accessing-gear-runtime).
* `fw_gear.manifest.Manifest` object, which represents the `manifest.json`
  that defines a gears metadata and _available_ runtime options. See more at
  [Accessing Gear Metadata](#accessing-gear-metadata-aka-manifestjson)
* `fw_gear.metadata.Metadata` object which represents the `.metadata.json`
  file. This file is a method of updating metadata on the Flywheel hierarchy
  _without_ needing a credentialed SDK client. Therefore the `Metadata` class is
  only useful in a non-SDK enabled gear, or a read-only SDK enabled gear. See
  more at [Writing Outputs](#writing-outputs)

## Basic Usage

`GearContext` is intended to be used as a context manager to be passed around.
For example, your python script entrypoint (e.g. `run.py`) could look something like:

```python
from fw_gear.context import GearContext
from my_awesome_module import do_something

def main(context):
    # Do something with your input dicom file
    do_something(
        dicom=context.config.get_input_path('dicom'),
        output_dir=context.output_dir
    )
if __name__ == "__main__":
    with GearContext() as context:
        # Setup basic logging
        context.init_logging()
        # Call my main function
        main(context)
```

## Accessing gear runtime

All _provided_ runtime configuration can be accessed via the `config` attribute,
which provides access to the [`Config`](./config.md) object that parses the
system-provided `config.json` file.

Example:

```python
with GearContext() as context
    # Get provided input object for input named `my-input`
    input1 = context.config.get_input('my-input')

    # Get path to input for input named `my-input2`
    input2_path = context.config.get_input_path('my-input-2')

    # Get provided configuration option value for `my-config`
    cfg = context.config.opts['my-config']
```

### Accessing gear runtime configuration options

You can the get the gear runtime configuration options from the `context.config.opts` dictionary.

```python
# Get the speed option value
my_speed = context.config.opts.get("speed")
```

### Accessing Inputs

You can get the full path to a named input file, or open the file directly:

```python
# Get the path to the input file named 'dicom'
dicom_path = context.config.get_input_path("dicom")
# Get the input filename
dicom_filename = context.config.get_input_filename("dicom")
# Open the dicom file for reading
with context.config.open_input("dicom", "rb") as dicom_file:
  dicom_data = dicom_file.read()
```

### Accessing Destination Container

You can get the destination container and the parent of the destination container
(e.g. to check at which level your analysis gear has been launched) using
`get_destination_container` and `get_destination_parent` methods. Example:

```python
destination = context.config.get_destination()
destination_parent = context.config.get_destination_parent()
```

!!! warning

    If your gear is not at least read-only SDK enabled, this will fail.
    See [API key input](./specs.md#api-key-input) for an example.

### Accessing the SDK Client

If your gear is an SDK gear (e.g. has an api-key input), you can easily access
an instance of the Flywheel SDK Client. Example:

```python
# Lookup a project using the client
project = context.client.lookup("my_group/Project 1")
```

## Accessing gear metadata (aka `.manifest.json`)

When the `manifest.json` is available in the gear at `/flywheel/v0`, the
`GearContext` provides an easy access to it. Example:

```python
gear_name = context.manifest.name
gear_version = context.manifest.version
```

!!! info
    The path `context.output_dir` is cleaned when the context manager exits with an
    exception. To disable this and retain files for inspection on error, enable
    debug mode using the [logger](#logging).

!!! note

    `manifest.json` is provided to the gear by the _user_ at build-time, i.e. as
    a step in the Dockerfile, whereas the `config.json` is provided to gear by
    the _system_ at run-time, i.e. mounted to the container.

    As such, the `GearContext` will only look in the `/flywheel/v0` folder as
    that is where the manifest is placed by convention (next to where the config
    is mounted at--`/flywheel/v0/config.json`)

## Writing Outputs

### Writing output file

The path to the output directory is available as an attribute on the `context`, and
helper methods exist for opening an output file for writing. By default, this output
directory will point to `/flywheel/v0/output`. Example:

```python
print('Output path: {}'.format(context.output_dir))
# prints "Output path: /flywheel/v0/output"

# Open an output file for writing
with context.open_output('out-file.dcm', 'wb') as f:
  f.write(dicom_data)
```

!!! note

    The path `context.output_dir` is cleaned when the context manager exits with
    an exception. To disable this and retain files for inspection on error,
    enable debug mode using the [logger](#logging).

### Writing metadata

#### Overview

Gears support writing metadata upon job completion back to Flywheel containers _without_
using the SDK. If a special file `.metadata.json` exists in the output container,
the json object inside will be uploaded as metadata.
With this feature, you can edit the destination container of the job runtime and the parent containers of the destination container _without_ needing to delve into the details of the SDK.

If you need to write metadata outside of the destination container and its parent containers, `fw_gear` provides several methods to do so.

!!! info

    To learn more how `.metadata.json` works, you can review the [.metadata.json spec](./specs.md#output-metadata)

#### NON-SDK enabled Method
<!-- TODO figure out to link to the API page for each method -->
##### **Custom container metadata (`update_container`)**

This method can be utilized to add free-form metadata on the specified
container, within the hierarchy.

* Arguments:
    * `container_type` (`str`): The container type.
    * `deep` (`bool`): If `True`, perform a deep (recursive) update on subdictionaries.
    * `**kwargs` (`dict`): Additional keyword arguments for update operations.

!!! info "Usage"

    ```python
        with fw_gear.GearContext() as context:
            # Update the destination container information
            info = {"my-metric": "my-value"}
            assert context.destination.type == 'analysis'
            context.metadata.update_container(context.destination.type, info=info)

            # Update the parent session of the destination analysis
            info = {"my-metric": "my-other-value"}
            context.metadata.update_container("session", label="Session 1", info=info)
    ```

##### **Custom file metadata (`update_file_metadata`)**

This method can be utilized to add free-form metadata to an input/output
or sibling file within the hierarchy.

* Arguments:
    * `file_` (`Any`): This can be the file name (a `str`), a SDK file object (`file.FileEntry`), or a dictionary representing the file that comes from `config.json`.
    * `deep` (`bool`): If `True`, perform a deep (recursive) update on subdictionaries.
    * `container_type` (_optional_, `str`): Type of the parent container.
    * `kwargs` (`dict`): Additional keyword arguments for update operations.

!!! info "Usage"

    ```python
        with fw_gear.GearContext() as context:
            # Set the modality and classification of an output file
            context.metadata.update_file_metadata(
                file_ = "out-file.dcm",  # NOTE: File must exist in output directory for this to work
                container_type="acquisition",
                modality="MR",
                classification={"Measurement": ["T1"]}
            )
    ```

##### **QC result for file (`add_qc_result`)**

This method can be utilized to add _qc_ result to an input/output
or sibling file within the hierarchy.

* Arguments:
    * `file_` (`Any`): This can be the file name (a `str`), a SDK file object (`file.FileEntry`), or a dictionary representing the file that comes from `config.json`.
    * `name` (`str`): The QC result name.
    * `state` (`str`): The state of the QC result. Can only set to
      `pass`, `fail` or `na`
    * `**data` (`dict`): Additional data/keyword arguments for the QC result.

!!! info "Usage"

    ```python

        add_info = {
            "parameter1": "value1",
            "parameter2": "value2"
         }

        with fw_gear.GearContext() as context:
            file_obj = context.config.get_input("<name-of-the-input-file>")

            context.metadata.add_qc_result(
                file_obj,
                "qc",
                "pass",
                **add_info
            )
    ```

    Doing this on a utility gear with an acquisition destination will produce metadata that looks like the following, with `<val>` replaced with the values from the specific gear

    ```json
    {
        "acquisition": {
            "files": [
                {
                    "name": "out_file.dcm",
                    "info": {
                        "qc": {
                            "<gear-name>": {
                                "job_info": {
                                    "version": "<gear-version>",
                                    "job_id": "62bc8cbcd98b86a919d60ead",
                                    "inputs": {<gear-inputs>},
                                    "config": {<gear-config>}
                                },
                                "my_qc": {
                                    "state": "PASS",
                                    "parameter1": "value1",
                                    "parameter2": "value2"
                                }
                            }
                        }
                    }
                }
            ]
        }
    }

    ```

!!! note

    * The `.metadata.json` is cleaned (e.g invalid JSON value), validated and written
    when the context manager exits.
    * The value written to the log will truncate long lists.
    * By default the metadata will be validated against the schema linked above
    and will mark the gear as failed if its invalid.  But you can turn that off
    by passing `fail_on_validation=False` to the `GearToolkitContext` initiator.
    * By using `.metadata.json` it only allows to update metadata that is
    stored under the destination container. In order to update metadata for file
    outside of the destination container, please use the SDK method (see below)
    instead.

##### **QC result for analysis (`add_qc_result_to_analysis`)**

This method can be utilized to add _qc_ result to the analysis
container during the job runtime.

* Arguments:
    * `name` (`str`): The QC result name.
    * `state` (`str`): The state of the QC result. Can only set to
      `pass`, `fail` or `na`
    * `**data` (`dict`): Additional data/keyword arguments for the QC result.

!!! info "Usage"

    ```python

        add_info = {
            "parameter1": "value1",
            "parameter2": "value2"
         }

        with fw_gear.GearContext() as context:

            context.metadata.add_qc_result(
                "analysis-qc",
                "pass",
                **add_info
            )
    ```

##### **File tags (`add_file_tags`)**

This method can be utilized to add tag(s) to an input/output or sibling.

* Arguments:
    * `file_` (`Any`): This can be the file name (a `str`), a SDK file
      object (`file.FileEntry`), or a dictionary representing the file
      that comes from `config.json`.
    * `tags` (`str`, Iterable[`str`]): Tag or list of tags to add to the
      specified file.

!!! info "Usage"

    ```python

        with fw_gear.GearContext() as context:
            file_obj = context.config.get_input("<name-of-the-input-file>")

            context.metadata.add_file_tags(
                file_obj,
                "tag-01"
            )
    ```

#### SDK enabled

##### **Custom container metadata (`modify_container_info`)**

This is a wrapper method for `flywheel.modify_container_info` SDK method
call. Using this method will update (which is the `set` method) metadata
of the specified container in Flywheel.

* Arguments:
    * `cont_id` (`str`): The container ID for the updated metadata.
    * `**data` (`dict`): Additional data/keyword arguments for the QC result.

!!! info "Usage"

    ```python

        new_info = {
            "infoA": "value1",
            "infoB": "value2"
         }

        with fw_gear.GearContext() as context:

            context.metadata.modify_container_info(
                "<container-id>",
                new_info
            )
    ```

##### **QC result (`add_qc_result_via_sdk`)**

This method can be used to add QC results or gear info for file that is
not stored under the destination container or within the job runtime
hierarchy.

* Arguments:
    * `cont_` (`Any`): Flywheel container object
    * `name` (`str`): The QC result name.
    * `state` (`str`): The state of the QC result. Can only set to
      `pass`, `fail` or `na`
    * `**data` (`dict`): Additional data/keyword arguments for the QC result.

!!! info "Usage"

    * **Add QC result for file that was used to trigger the gear.**

        ```python

        with fw_gear.GearContext() as context:

            context.metadata.add_qc_result_via_sdk(cont_='input_file.dcm', "input_qc", state="PASS", {'my-result': 'test'})
        ```

    * **Add qc result to specified Flywheel container info.**

        ```python
        # Get an acquisition container
        acquisition_cont = client.get_acquisition("<acquisition-id>")

        with fw_gear.GearContext() as context:
            context.metadata.add_qc_result_via_sdk(cont_=acquisition_cont, "input_qc", state="PASS",{'my-result': 'test'})
        ```

###### Example

Below is an example code that do the following actions:

* Update destination container custom information
* Update the output file `out-file.dcm` modality and classification
* Update the `session` container label and custom information

```python
with fw_gear.GearContext() as context:
    # Update the destination container custom information
    info = {"my-metric": "my-value"}
    context.metadata.update_container(context.destination.type, info=info)
    # Set the modality and classification of an output file
    context.metadata.update_file_metadata(
        "out-file.dcm",  # NOTE: File must exist in output directory fo this to work
        modality="MR",
        classification={"Measurement": ["T1"]}
    )
    # Update the any parent container. Example:
    info = {"my-metric": "my-other-value"}
    context.metadata.update_container("session", label="Session 1", info=info)
```

After running the code above, a `.metadata.json` file will be generated.

_Note_:  In this example, it is being run in an **analysis** gear

```json
{
    'analysis': {
        'info': {'my-metric': 'my-value'},
        'files': [
            'out-file.dcm': {
                'modality': 'MR',
                'classification': {'Measurement': ['T1']}
            }
        ]
    },
    'session': {
        'info': {"my-metric": "my-other-value"},
        'label': 'Session 1'
    }
}
```

## Logging

Calling `context.init_logging()` will configure python logger to log message
at INFO level. If your `manifest.json` defines a boolean `debug` option, then
it `init_logging()` will use this value to set the logging level to DEBUG when
`debug` is `True`.

```python
with GearToolkitContext() as context:
    # Setup basic logging
    context.init_logging()
```

## SDK Profiling

With `flywheel-sdk` >= 16.0.0, the `GearContext` context manager
will automatically report out API usage of your gear when `debug` config option
is enabled in the `config.json`. Example:

```python
import logging
log = logging.getLogger(__name__)
from flywheel_gear_toolkit import GearToolkitContext
with GearToolkitContext() as context:
  context.init_logging()
  proj = context.client.lookup('<group>/<project.label>')
  log.info(f"Found project: {proj.id}")
```

will log

```python
[ 20210701 12:52:06     INFO flywheel_gear_toolkit.logging: 219 - configure_logging()  ] Log level is DEBUG
[ 20210701 12:52:07     INFO __main__: 4 - <module>()  ] Found project: 603413543321ab021ef0a0a7
[ 20210701 12:52:07    DEBUG flywheel_gear_toolkit.context.context: 618 - __exit__()  ] SDK usage:
{'GET': {'https://ga.ce.flywheel.io:443/api/version': 1},
'POST': {'https://ga.ce.flywheel.io:443/api/lookup': 1}}
```

## Modify File

### Sanitize Filename (`sanitize_label`)

This method can be used to sanitize and truncate strings to ensure
it is compatible with the filesystem directory or filename requirements.  It replaces invalid characters and ensures the length does not exceed 255 characters.

Heres what the function does:

* Replaces any asterisks (*) with the word "star".
* Invalid characters (e.g.,*, /, \, and other non-printable characters) are substituted with underscores (_).
* Truncates the string to a maximum of 255 characters.

!!! info "Usage"

* Arguments:
    * `value` (`str`): The input string that represents the filename or
      directory label to be sanitized.

* Returns:
    * A cleaned and shortened version of the input string, with invalid characters replaced and the string limited to 255 characters.

!!! info "Usage"

    * **Sanitize a filename.**

        ```python

        from fw_gear.utils import sanitize_label

        sanitize_filename = sanitize_label("Invalid*Label/With:Forbidden\\Characters")
        print(filename)

        # Output: "InvalidstarLabel_With_Forbidden_Characters"

        ```
