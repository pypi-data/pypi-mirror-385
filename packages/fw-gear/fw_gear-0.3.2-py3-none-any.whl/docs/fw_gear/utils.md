# Miscellaneous Helper Method

This documentation highlights several useful method calls under
`fw_gear.utils`, detailing their functionality and usage.

## Gear Run Helper Method

* `setup_gear_run()` method can be used to gather necessary gear documents
object and configurations/inputs arguments. This method can be used
during the runtime of a gear or outside of the gear context

    Use Case:

    Here is an example of using the method to setup gear configuration
    for running `dicom-fixer` gear via SDK.

    !!! info "Example"

        ```python

        import flywheel

        import os
        import fw_gear.utils.sdk_helpers as gear_utils

        API_KEY=os.environ.get("FW_API_KEY")
        client = flywheel.Client(API_KEY, root=True)

        dcm_ins_file = client.get_file(<file-id>)

        geardoc, ins_dict, config_dict = gear_utils.setup_gear_run(client,
                                "dicom-fixer",         # name of the gear to run
                                {"dicom":dcm_ins_file, # gear input file
                                "debug":True,         # gear configuration
                                "tag":"test-run"      # gear configuration
                                })

        # Launch the gear with the return values
        # In this use case, the destination will be the parent of the input-file
        parent_cont=dcm_ins_file.parent_ref.get("type")
        geardoc.run(inputs=ins_dict, config=config_dict, destination=parent_cont)
        ```

        The call above will return a Flywheel `GearDocument`
        object, input dictionary for the gear run
        and configuration dictionary for the gear configuration.

    This method can be used within a gear run as well.
    Below is a quick example

    !!! info "Example"

        ```python

        import fw_gear.utils.sdk_helpers as gear_utils


        with fw_gear.GearContext() as context:

            # use the gear runtime input file as the dicom-fixer input file
            in_file_id = context.config.get_input("inputA").get("hierarchy").get("id")
            in_file_obj = context.client.get_file(in_file_id)

            geardoc, ins_dict, config_dict = gear_utils.setup_gear_run(client,
                                    "dicom-fixer",         # name of the gear to run
                                    {"dicom":dcm_ins_file, # gear input file
                                    "debug":True,         # gear configuration
                                    "tag":"test-run"      # gear configuration
                                    })

            # Launch the gear with the return values
            # In this use case, the destination will be the parent of the input-file
            parent_cont=in_file_obj.parent_ref.get("type")
            geardoc.run(inputs=ins_dict, config=config_dict, destination=parent_cont)
        ```

## Command Wrapper Helper Method

* `exec_command()` (from `fw_gear.utils.wrapper`) runs external commands with optional
  live streaming, safer shell handling, and optional tee-to-file.
  It returns `(stdout, stderr, returncode)` and raises `RuntimeError`
  if the command exits non-zero.

    **Key behavior:**

  * When `stream=True`, output is streamed live; `stderr` is merged into `stdout`
      during streaming to avoid deadlocks. The returned `stderr` will be empty
      in this mode.
  * When `shell=True`, arguments are safely quoted except for literal redirection tokens
      (e.g., `>`, `>>`, `2>&1`). If redirection tokens are present,
      live streaming is disabled.
  * `environ` merges over the current process environment (preserves `PATH`).
  * `stdin` is set to `DEVNULL` to prevent interactive blocking.
  * If `logfile` is provided, the full, unfiltered stream is appended to that file.

    **Parameters (commonly used):**

  * `command: List[str]` — program and args (`["du", "-h"]`).
  * `stream: bool` — stream output live (default `False`).
  * `stream_mode: Optional[str]` — `"all"`, `"filter_only"`, or `"throttled"`.
      Use `throttle_sec` to rate-limit non-important lines.
  * `logfile: Optional[str|Path]` — tee full stream to a file (append).
  * `shell: bool` — enable shell parsing/redirects; see notes above.
  * `environ: Optional[Dict[str,str]]` — extra env vars (merged).

    **Use Cases:**

    !!! info "Example — basic run (buffered)"
        Capture separate `stdout` / `stderr` and check the return code.
        ```python
        from fw_gear.utils.wrapper import exec_command

        stdout, stderr, rc = exec_command(["du", "-h", "/var/log"])
        if rc == 0:
            print("Done:\n", stdout)
        ```

    !!! info "Example — live stream important lines only"
        Stream important lines in real time (as defined by the internal filter),
        tee the full unfiltered stream to a file, still return the complete transcript.
        ```python
        stdout, stderr, rc = exec_command(
            ["my-long-task", "--verbose"],
            stream=True,
            stream_mode="filter_only",   # only print important lines
            logfile="my-long-task.stream.log",
        )
        ```

    !!! info "Example — throttled streaming (reduce spam)"
        Rate-limit non-important lines while always showing important ones.
        ```python
        stdout, stderr, rc = exec_command(
            ["trainer", "--epochs", "50"],
            stream=True,
            stream_mode="throttled",
            throttle_sec=1.5,
        )
        ```

    !!! info "Example — shell redirects (no streaming)"
        Use the shell for redirects/pipes.
        Streaming is disabled when redirects are present.
        ```python
        cmd = ["du", "-h", "/var/log", ">>", "du.out.log", "2>&1"]
        stdout, stderr, rc = exec_command(cmd, shell=True, stream=False)
        ```

    !!! info "Example — custom environment"
        Overlay specific variables while keeping `PATH` and others intact.
        ```python
        stdout, stderr, rc = exec_command(
            ["bash", "-lc", "echo $MY_FLAG && which python"],
            environ={"MY_FLAG": "1"},
            shell=True
        )
        ```

    **Notes:**

  * Use `stream=False` if you need `stderr` separated in the return tuple.
  * `logfile` appends to the given path; rotate or truncate externally if needed.
  * On failure, the function logs the error output and raises `RuntimeError`.

!!! tip "Overriding the important-line filter (`_ALWAYS_PRINT_RE`)"
    You can override which lines are treated as important during live streaming
    by setting the `EXEC_ALWAYS_PRINT_RE` environment variable **before import**,
    or by reassigning the compiled regex at runtime.

    **Python (set before import)**
    ```python
    import os
    # Print error, failed, timeout, warn/warning as important
    os.environ["EXEC_ALWAYS_PRINT_RE"] = r"\b(error|failed|timeout|warn(?:ing)?)\b"

    from fw_gear.utils.wrapper import exec_command
    ```

    **Dockerfile**
    ```dockerfile
    # Dockerfile
    ENV EXEC_ALWAYS_PRINT_RE="\b(error|failed|timeout|warn(?:ing)?)\b"
    ```

    **Override in Python (advanced)**
    If you must change it **after import**, recompile and assign the module variable:
    ```python
    import re
    import fw_gear.utils.wrapper as wrapper

    wrapper._ALWAYS_PRINT_RE = re.compile(
        r"\b(error|failed|timeout|warn(?:ing)?)\b",
        re.I,
    )
    ```
