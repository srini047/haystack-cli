# `haystack-cli`

The CLI for Haystack Agentic AI Framework.

**Usage**:

```console
$ haystack [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `config`: Manage Haystack CLI configuration.
* `init`: Scaffold a new Haystack project.
* `pipeline`: Manage and run Haystack pipelines.
* `component`: Browse and inspect Haystack components.
* `document`: Inspect documents in the configured...

## `haystack config`

Manage Haystack CLI configuration.

**Usage**:

```console
$ haystack config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `show`: Print all resolved config values,...
* `get`: Read a single config value
* `set`: Set a config key to a value
* `schema`: Show all valid config keys and their...
* `edit`: Open the config file in $EDITOR or default...
* `init`: Interactively create a project or global...

### `haystack config show`

Print all resolved config values, annotated with their source.

**Usage**:

```console
$ haystack config show [OPTIONS]
```

**Options**:

* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack config get`

Read a single config value

**Usage**:

```console
$ haystack config get [OPTIONS] KEY
```

**Arguments**:

* `KEY`: [required]

**Options**:

* `--help`: Show this message and exit.

### `haystack config set`

Set a config key to a value

**Usage**:

```console
$ haystack config set [OPTIONS] KEY VALUE
```

**Arguments**:

* `KEY`: [required]
* `VALUE`: [required]

**Options**:

* `--global`: Write to global config.
* `--help`: Show this message and exit.

### `haystack config schema`

Show all valid config keys and their accepted values

**Usage**:

```console
$ haystack config schema [OPTIONS]
```

**Options**:

* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack config edit`

Open the config file in $EDITOR or default to `nano`.

**Usage**:

```console
$ haystack config edit [OPTIONS]
```

**Options**:

* `--global`: Edit global config.
* `--help`: Show this message and exit.

### `haystack config init`

Interactively create a project or global config file.

**Usage**:

```console
$ haystack config init [OPTIONS]
```

**Options**:

* `--global`: Initialise global config.
* `--help`: Show this message and exit.

## `haystack init`

Scaffold a new Haystack project.

**Usage**:

```console
$ haystack init [OPTIONS] [PROJECT_NAME] COMMAND [ARGS]...
```

**Arguments**:

* `[PROJECT_NAME]`

**Options**:

* `--help`: Show this message and exit.

## `haystack pipeline`

Manage and run Haystack pipelines.

**Usage**:

```console
$ haystack pipeline [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Guided wizard to create a new pipeline...
* `validate`: Validate a pipeline YAML — checks...
* `inspect`: Show components, connections, and...
* `show`: Visualize a pipeline as ASCII (default),...
* `save`: Save a PNG diagram of the pipeline to...
* `benchmark`: Run a benchmark on the pipeline and print...
* `diff`: Semantically diff two pipeline YAML files
* `run`: Execute a pipeline.
* `template`: Work with pipeline templates.

### `haystack pipeline create`

Guided wizard to create a new pipeline YAML from a template

**Usage**:

```console
$ haystack pipeline create [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `haystack pipeline validate`

Validate a pipeline YAML — checks structure and component types

**Usage**:

```console
$ haystack pipeline validate [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to pipeline YAML.  [required]

**Options**:

* `--help`: Show this message and exit.

### `haystack pipeline inspect`

Show components, connections, and input/output sockets of a pipeline

**Usage**:

```console
$ haystack pipeline inspect [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to pipeline YAML.  [required]

**Options**:

* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack pipeline show`

Visualize a pipeline as ASCII (default), Mermaid text, or JSON adjacency

**Usage**:

```console
$ haystack pipeline show [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to pipeline YAML.  [required]

**Options**:

* `-f, --format TEXT`: Output format: ascii | mermaid.  [default: ascii]
* `--json`: Output graph as JSON adjacency list.
* `--help`: Show this message and exit.

### `haystack pipeline save`

Save a PNG diagram of the pipeline to assets/pipelines/&lt;name&gt;.png

**Usage**:

```console
$ haystack pipeline save [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to pipeline YAML.  [required]

**Options**:

* `--help`: Show this message and exit.

### `haystack pipeline benchmark`

Run a benchmark on the pipeline and print results

**Usage**:

```console
$ haystack pipeline benchmark [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to pipeline YAML.  [required]

**Options**:

* `-i, --input TEXT`: Pipeline inputs as JSON string.
* `--input-file PATH`: Path to JSON file with inputs.
* `-n, --runs INTEGER`: Number of benchmark runs.  [default: 10]
* `--warmup INTEGER`: Warmup runs excluded from stats.  [default: 1]
* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack pipeline diff`

Semantically diff two pipeline YAML files

**Usage**:

```console
$ haystack pipeline diff [OPTIONS] FILE_A FILE_B
```

**Arguments**:

* `FILE_A`: First pipeline YAML.  [required]
* `FILE_B`: Second pipeline YAML.  [required]

**Options**:

* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack pipeline run`

Execute a pipeline. Pass inputs via --input JSON or --input-file

**Usage**:

```console
$ haystack pipeline run [OPTIONS] FILE
```

**Arguments**:

* `FILE`: Path to pipeline YAML.  [required]

**Options**:

* `-i, --input TEXT`: Pipeline inputs as JSON string.
* `--input-file PATH`: Path to JSON file with inputs.
* `--dry-run`: Validate and load only — do not execute.
* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack pipeline template`

Work with pipeline templates.

**Usage**:

```console
$ haystack pipeline template [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all available built-in pipeline...
* `use`: Copy a pipeline template into the project...

#### `haystack pipeline template list`

List all available built-in pipeline templates

**Usage**:

```console
$ haystack pipeline template list [OPTIONS]
```

**Options**:

* `--json`: Output as JSON.
* `--help`: Show this message and exit.

#### `haystack pipeline template use`

Copy a pipeline template into the project (default: pipelines/)

**Usage**:

```console
$ haystack pipeline template use [OPTIONS] NAME
```

**Arguments**:

* `NAME`: [required]

**Options**:

* `-o, --output PATH`: Output directory.
* `--help`: Show this message and exit.

## `haystack component`

Browse and inspect Haystack components.

**Usage**:

```console
$ haystack component [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List all available Haystack components,...
* `info`: Show full schema, init params, and sockets...

### `haystack component list`

List all available Haystack components, grouped by type.

**Usage**:

```console
$ haystack component list [OPTIONS]
```

**Options**:

* `-t, --type TEXT`: Filter by category.
* `-s, --search TEXT`: Search by keyword.
* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack component info`

Show full schema, init params, and sockets for a component.

**Usage**:

```console
$ haystack component info [OPTIONS] NAME
```

**Arguments**:

* `NAME`: [required]

**Options**:

* `--json`: Output as JSON.
* `--help`: Show this message and exit.

## `haystack document`

Inspect documents in the configured document store.

**Usage**:

```console
$ haystack document [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `list`: List documents in the configured document...
* `search`: Search documents in the configured...

### `haystack document list`

List documents in the configured document store.

**Usage**:

```console
$ haystack document list [OPTIONS]
```

**Options**:

* `-n, --limit INTEGER`: Max documents to show.  [default: 20]
* `--filter-field TEXT`: Meta field to filter on.
* `--filter-value TEXT`: Value to match.
* `--json`: Output as JSON.
* `--help`: Show this message and exit.

### `haystack document search`

Search documents in the configured document store.

**Usage**:

```console
$ haystack document search [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: [required]

**Options**:

* `-k, --top-k INTEGER`: Number of results.  [default: 5]
* `--json`: Output as JSON.
* `--help`: Show this message and exit.
