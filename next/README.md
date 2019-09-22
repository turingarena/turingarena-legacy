# Ideas for next TuringArena

We expose several APIs, implemented in Rust with C bindings.

## Metadata

Metadata is a TOML file which is used to share any data between different components.
For example, a numeric constant may be shared among the problem statement, program interface (to be hardcoded in templates), and evaluator.

`Metadata::Context`: configuration on how metadata is loaded.

* `load()`: loads and return the metadata. Reusing the context allow it to be cached in-memory.

## Sandbox

`Sandbox::Context`: configuration and data used to start sandboxes,
such as caches, a mapping from file extensions to language, compiler options, global hard resource limits (for safety only, not grading), etc.
May use a `Metadata::Context` to load the configuration.

* `load(path)`: compiles source at `path`, if needed, and returns a `Sandbox::Program`. Source language is determined from file name (and/or other info such as she-bang), according to configuration of this context. NB: if compilation fails due to the errors in the source, this method does *not* fail. Instead, it returns a program which, when executed, returns an already-terminated sandbox. (Rationale: potentially avoids redundant error checking.)

`Sandbox::Program`: a runnable program.

* `run()`: runs this program within a sandbox, and returns a `Sandbox::Process`.
* `exec()`: runs this program directly, without a sandbox, in this very process if possible (i.e., using UNIX `exec`).

`Sandbox::Process`: a process running in the sandbox.

* `write(data)`: sends data to `stdin` (TODO: use byte arrays or strings?)
* `read_line(maxlen, timeout)`: receives the next line from `stdout` (TODO: use byte arrays or strings? allow custom separator? add call that reads exactly *n* bytes?)
* `peek(options)`: get the current state of the process, and returns a `Sandbox::ProcessState`. Parameters `options` configures what informations are needed. (Rationale: repeatedly getting CPU time/memory usage may be expensive in a loop, so it is optional, but we stick to a single method to coalesce expensive operations together, such as stopping the process with `SIGSTOP`.)
* `close(timeout, options)`: waits the termination of the process, if still running, and killing it if timeout expires. Returns the process state after the termination. (Parameters `options` configures what informations are needed.) Releases resources, and must always be called at the end, exactly once, for every process.

`Sandbox::ProcessState`: a structure with info about the state of a running sandbox process, at a given time.

* `termination`: if the process is not running, contains a structure that explains why (e.g., "Exited normally", "Exited with return code ...", "Still running after timeout, killed", "Terminated by signal ...", "Process never started due to compilation errors.")
* `cpu_time`: current CPU time usage. Only reliable when computing the difference between two `peek()` calls.
* `current_memory`: current memory usage. Only meaningful in a `peek()` call, as it is zero after termination.
* `peak_memory`: peak memory usage since last `peek()` call which read this value. Asking for this value implicitly resets the peak watermark to zero.


## Sandbox CLI

A CLI tool runs a program within a sandbox, forwarding `stdin` and `stdout` to the process via sandbox API.

Regularly, data is flushed to `stdout` with `write()` and `stdin` is polled with `read_line()`.
If the timeout is reached when polling, the reading of `stdin` stops, and a message is printed to `stderr` to notify this situation.
The polling resumes when new data is sent to `stdout`.

When a special signal is received, the current process state (obtained using `peek()`) is dumped on `stderr`, and the polling of `stdin` resumes (even if nothing was sent to `stdout`).

On `SIGTERM` or `SIGHUP`, the sandbox is closed calling `close()`, and the state is dumped to stderr.

The sandbox CLI may also create named pipes as an alternative method to send data to the process.

## Submission / Evaluation

Even if using SEGI to communicate with the evaluator,
when using Rust or its C bindings, submission and evaluations are mapped to the same type of structures on both sides.
In particular, the API allows producing evaluations without using SEGI (say, in unit tests).

`LocalSubmission`: maps each submission field to a path on the local filesystem.

`NetworkSubmission`: maps each submission field to a pair of file name, sanitized (i.e., short, without `/`, possibly alphanumeric-only, but preserving file extension), and file content (TODO: as byte array? assume UTF-8?). Differently from Web API `File`s, the MIME type is always implicit in the file name extension. (Rationale: otherwise, we need to complicate local submissions to store MIME-type.)

`EvaluationEvent`: a wrapper on the JSON object representing an evaluation event.

Evaluations would probably use some native Rust type for streams of objects.

## Driver

Interface definition language is changed as follows.

* Each function has exactly one call site, and is declared implicitly when it is called.
* Function arguments must be identifiers, not expressions, and they determine the name and type of the respective parameter.
This simplifies variable resolution: each variable is resolved the first time its name occurs, as it is, as an argument to a function call.
* A new construct `let <var> = <expr>;` is added.
This allows passing the result of expressions as function arguments, overcoming this new limitation.
Variable resolution does not occur in this case.
* Named scalar types may be added, since the special syntax to express array types in function declarations is no longer required.

The driver is implemented by generating at compile-time a representation of the interface as a type-safe abstract state machine.
Namely, there are two types of states, those waiting for the evaluator input, and those waiting for the process output.
Evaluator input consists of a call to an interface function, or other control events such as returning from a callback or exiting the process.
When a transition occurs, it may result in the generation of input data to send to the process and/or the result of a function call or the call to a callback.

Type safety is obtained by associating each of the states with a generated type.
This type has methods that represent only the valid transitions from the state, which consume the current state and return the next.
