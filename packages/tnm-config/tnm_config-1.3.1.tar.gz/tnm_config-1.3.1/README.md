# tnm-config

A  lightweight  configuration loader for Python.
Supports **YAML**, **JSON**, **XML** (and is pluggable for other formats). Features environment-backed values, filesystem paths, optional typed validation (Pydantic models or dataclasses), and a loader registry for plugins.

---

## Install

Basic

```bash
pip install tnm-config
```

Optional extras:

```bash
pip install "tnm-config[yaml]"     # PyYAML support
pip install "tnm-config[xml]"      # xmltodict support
pip install "tnm-config[all]"      # yaml + xml + pydantic extras (if provided)
```

If you want `schema_type` validation with Pydantic models:

```bash
pip install pydantic
```

---

## Quick API

Import:

```py
from pathlib import Path
from tnm.config import ConfigLoader
from tnm.config.errors import ConfigError

```

Basic usage:

```py
loader = ConfigLoader(Path("config/example_config.yaml"))

# Raw resolved dict/list/scalar
cfg = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd())

# With schema (pydantic model or dataclass):
cfg_obj = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd(), schema_type=MyModel)
```

Type hint behaviour:

* If `schema_type is None`: return is a parsed JSON-like type (`dict | list | str | int | ...`).
* If `schema_type` supplied: return is `schema_type`.

---

## Supported file marker syntax

### Environment-backed values

These let you source values from environment variables with a type hint.

YAML:

```yaml
hosts: !env [ ES_HOSTS, list:url, http://127.0.0.1:9200 ]
```

JSON:

```json
"hosts": { "__env__": ["ES_HOSTS", "list:url", "http://127.0.0.1:9200"] }
```

XML:

```xml
<hosts>
  <env var="ES_HOSTS" type="list:url" default="http://127.0.0.1:9200"/>
</hosts>
```

Supported casts:

* `str`, `int`, `float`, `bool`
* `url` (validates that parsed URL has scheme + host)
* `list:str`, `list:url` (comma separated values)

If env var not set and no default provided, a `EnvVarNotSetError` is raised.

---

### Project-relative paths & preserved tokens

YAML `!path` and JSON/XML mapping variants are supported.

YAML:

```yaml
templates_dir: !path extras/templates
```

JSON:

```json
"templates_dir": { "__path__": { "value": "extras/templates" } }
```

XML:

```xml
<templates_dir>
  <path value="extras/templates"/>
</templates_dir>
```

**Preserved tokens** inside strings are supported in both `%token%` and `{{ token }}` forms:

* `%project_root%`, `%project_dir%`, `{{ project_root }}`  resolved via caller `project_root_callback()`.
* `%home%`, `%user_home%`, `{{ home }}` the current OS user's home directory
* `%user%`, `%username%`, `{{ user }}` same as `home` token

You can mix tokens with path fragments:

```yaml
templates_dir: "%project_root%/extras/templates"
local_cache: "{{ home }}/.myapp/cache"
```

You may also use an explicit mapping form (recommended for JSON/XML):

```json
"templates_dir": {
  "__path__": {
    "value": "{{project_root}}/data/json/es_queries"
  }
}
```

**Important:** when resolving tokens that require the project's root (e.g. `%project_root%`) you **must** pass a zero-argument callable `project_root_callback` to `load(...)`. Example:

```py
cfg = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd())
```

If a token requires the project root but you didn't provide the callback, `ConfigError` will be raised with a helpful message.

---

## Example config files

YAML (`example_config.yaml`):

```yaml
elasticsearch:
  hosts: !env [ ES_HOSTS, list:url, http://127.0.0.1:9200 ]
  username: !env [ ES_USERNAME, str, demo_user ]
  password: !env [ ES_PASSWORD, str, demo_pass ]
  templates_dir: !path "{{project_root}}/extras/templates"
  timeout: 10
  version: 8.15
```

JSON (`example_config.json`):

```json
{
  "elasticsearch": {
    "hosts": { "__env__": ["ES_HOSTS", "list:url", "http://127.0.0.1:9200"] },
    "username": { "__env__": ["ES_USERNAME", "str", "demo_user"] },
    "password": { "__env__": ["ES_PASSWORD", "str", "demo_pass"] },
    "templates_dir": { "__path__": { "value": "{{project_root}}/extras/templates" } },
    "timeout": 10,
    "version": 8.15
  }
}
```

XML (`example_config.xml`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<elasticsearch>
    <hosts>
        <env var="ES_HOSTS" type="list:url" default="http://127.0.0.1:9200"/>
    </hosts>
    <username>
        <env var="ES_USERNAME" type="str" default="demo_user"/>
    </username>
    <password>
        <env var="ES_PASSWORD" type="str" default="demo_pass"/>
    </password>
    <templates_dir>
        <path value="{{project_root}}/extras/templates"/>
    </templates_dir>
    <timeout>10</timeout>
    <version>8.15</version>
</elasticsearch>
```

All three examples are semantically equivalent. Scalar values (numbers, strings, booleans) may be present anywhere and will be returned as-is.

---

## Typed schemas (validation)

You can pass a `schema_type` to `load(...)`. Supported schema types:

* Pydantic `BaseModel`.
* Plain Python `dataclass`.
* Any callable/class that accepts the resolved dict or scalar in its constructor.

```py
from pydantic import BaseModel
from tnm.config import ConfigLoader

class ElasticCfg(BaseModel):
    hosts: list[str]
    username: str | None = None
    password: str | None = None
    templates_dir: str | None = None

loader = ConfigLoader(Path("config/example_config.yaml"))
cfg_obj = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd(), schema_type=ElasticCfg)
```

If validation fails, a `ConfigError` is raised (with the underlying validation exception as `__cause__`).

---

## Loader registry & plugin entry-point

There is a loader registry so additional formats can be added.

Runtime registration:

```py
from tnm.config.loaders import register_loader, get_loader_for_suffix

register_loader(".ini", lambda: MyIniLoader())
loader = get_loader_for_suffix(".ini")
data = loader.load(Path("config.ini"), project_root_callback=lambda: Path.cwd())
```

---

## Errors & exceptions

All package-specific exceptions are subclasses of `tnm.config.errors.ConfigError`.

Key exceptions:

* `ConfigError` – generic parse/resolve/validation error (base).
* `EnvVarNotSetError` – env var referenced by `!env`/`__env__`/`<env/>` is not set and no default provided.
* `InvalidURLError` – env var declared as `url` is invalid.

Usage:

```py
from tnm.config import ConfigLoader, ConfigError

try:
    cfg = ConfigLoader(Path("config.yaml")).load("elasticsearch", project_root_callback=my_cb)
except ConfigError as exc:
    # inspect exc.__cause__ for underlying error details (if any)
    print("Config failed:", exc)
```

---

## Security & safety

* YAML parsing uses `safe_load` and custom safe constructors. Do **not** parse untrusted YAML.
* Be cautious with logging or printing secrets from config (passwords, tokens).
* When using `schema_type`, underlying validation errors are preserved in `__cause__` to help debugging — avoid leaking them to users.

---

**Using preserved tokens:**

`es.yaml`:

```yaml
elasticsearch:
  templates_dir: "%project_root%/extras/templates"
  backup_dir: "{{ home }}/.cache/myapp/backups"
```

Load:

```py
cfg = ConfigLoader(Path("es.yaml")).load("elasticsearch", project_root_callback=lambda: Path("/srv/myclient"))
```

---

## Contributing & roadmap

Possible next steps:

* Add `dacite` optional extra for full dataclass support (nested dataclasses).
* Add `tnm-config-validate` CLI to validate a config against a schema.
* Add caching for parsed config and file watch invalidation.
* Add small JSON Schema adapter for validating raw config shapes.

Contributions via PRs are welcome.

---

## License

MIT
