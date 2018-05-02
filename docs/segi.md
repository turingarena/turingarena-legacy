# Submission Evaluation Gateway Interface (SEGI)

The **Submission Evaluation Gateway Interface (SEGI)**
is a protocol to communicate with an evaluator in order to evaluate a submission, inspired by the Common Gateway Interface (CGI) for responding to HTTP requests.

SEGI is a low-level interface:
it is designed to easily integrate evaluators written using different programming languages and technologies,
as it relies only on the abstraction offered by POSIX.

## General assumptions

- Evaluations occur sequentially in a (POSIX) process.
    - For each submission to evaluate, the evaluator program is executed once.
    How the evaluator program is loaded and started is not specified by SEGI.
    Possible options:
        - Launching an executable as a child process.
        - Running a Python script in an existing Python interpreter process.
        - ...
    - At most one submission is evaluated in the same process at the same time.
    (But more than one submission may be evaluated in the same process sequentially.)
    - The evaluation stops when the evaluator program terminates.
    How the termination of the evaluator program is determined is not specified by SEGI.
- The communication with the evaluator program occurs only through the process context.
Specifically:
    - No extra arguments depending on the submission are passed directly to the evaluator program
    (say, function arguments).
    - No output is taken directly from the evaluator program
    (say, function return value).
    - All the communication occurs through:
        - enviroment variables,
        - standard file descriptors, and
        - files on the local filesystem, whose path is specified in enviroment variables.
    - Other data can be provided to the evaluator program, preferably through enviroment variables,
    as long as they do not depend on the submission.

### Rationale

Thanks to the above assumptions, the evaluator program can easily invoke other executables (as child processes)
as part of the evaluation.
Indeed, all the relevant process context (enviroment variables and standard file descriptors)
is inherited by child processes by default.

SEGI, as CGI, has the drawback of introducing overhead
due to the usage of system calls for process management.
However, while this overhead may be significant for HTTP requests,
it is totally negligible for submission evaluations,
which are supposed to be infrequent and take up to a few seconds.
Also, the security implications of CGI,
such as the ability to set some enviroment variables to arbitrary values,
are a lesser concern for SEGI since the evaluator code
is already considered unsafe, and it is run in a container.

## Submission

For each field in the submission, an enviroment variable is provided.

- If the field is of type *string*, the variable is defined by:
    - name: `SUBMISSION_VALUE_` followed by the field name *to upper case*,
    - value: the string value of the field (verbatim).
- If the field is of type *file*, the variable is defined by:
    - name: `SUBMISSION_FILE_` followed by the field name *to upper case*,
    - value: the *absolute* path to a *regular* file on the filesystem
    whose content is the value of the field.
    (The process must be able to open the file for reading.)

**Example.**
For a submission with two fields
    
- name: `source_language`, type: *string*, value: `c++`
- name: `source`, type: *file*

the content of the file in `source` is saved to
a temporary file `/tmp/submission_42/source.cpp`
and two environment variables are provided to the evaluator:
    
    SUBMISSION_VALUE_SOURCE_LANGUAGE=c++
    SUBMISSION_FILE_SOURCE=/tmp/submission_42/source.cpp

## Evaluation text

TODO

## Evaluation data

TODO