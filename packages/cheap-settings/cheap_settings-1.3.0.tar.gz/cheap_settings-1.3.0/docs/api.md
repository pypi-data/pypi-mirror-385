# API Reference

## CheapSettings

::: cheap_settings.CheapSettings
    options:
      show_root_heading: true
      show_root_toc_entry: false
      heading_level: 3

## Type Support

`cheap-settings` automatically converts environment variable strings to the appropriate Python types based on type annotations.

### Supported Types

| Type | Example | Environment Variable | Notes |
|------|---------|---------------------|-------|
| `str` | `"hello"` | `VALUE="hello"` | No conversion needed |
| `int` | `42` | `VALUE="42"` | Converted with `int()` |
| `float` | `3.14` | `VALUE="3.14"` | Converted with `float()` |
| `bool` | `True` | `VALUE="true"` | Accepts: true/false, yes/no, on/off, 1/0 (case-insensitive) |
| `pathlib.Path` | `Path("/etc")` | `VALUE="/etc"` | Converted with `Path()` |
| `datetime` | `datetime(2024, 12, 25, 15, 30)` | `VALUE="2024-12-25T15:30:00"` | ISO format (fromisoformat) |
| `date` | `date(2024, 12, 25)` | `VALUE="2024-12-25"` | ISO format (YYYY-MM-DD) |
| `time` | `time(15, 30, 45)` | `VALUE="15:30:45"` | ISO format (HH:MM:SS) |
| `Decimal` | `Decimal("99.99")` | `VALUE="99.99"` | Preserves precision |
| `UUID` | `UUID("...")` | `VALUE="550e8400-..."` | With/without hyphens |
| `list` | `[1, 2, 3]` | `VALUE='[1, 2, 3]'` | Parsed as JSON |
| `dict` | `{"key": "value"}` | `VALUE='{"key": "value"}'` | Parsed as JSON |
| `Optional[T]` | `None` or `T` | `VALUE="none"` or valid `T` | Special "none" string sets to None |
| `Union[T, U]` | `T` or `U` | Valid for either type | Tries each type in order |

### Extended Type Examples

#### Date and Time Types

```python
from datetime import datetime, date, time
from cheap_settings import CheapSettings

class TimeSettings(CheapSettings):
    created_at: datetime = datetime(2024, 1, 1)
    expiry_date: date = date(2024, 12, 31)
    backup_time: time = time(3, 0, 0)

# Environment variables:
# CREATED_AT="2024-12-25T15:30:45.123456"  # With microseconds
# CREATED_AT="2024-12-25T15:30:45+05:30"   # With timezone
# EXPIRY_DATE="2025-01-01"
# BACKUP_TIME="02:30:00"
```

#### Decimal for Financial Precision

```python
from decimal import Decimal

class PricingSettings(CheapSettings):
    product_price: Decimal = Decimal("99.99")
    tax_rate: Decimal = Decimal("0.0825")  # 8.25%

# Preserves exact decimal precision
# PRODUCT_PRICE="149.99"
# TAX_RATE="0.0925"

# Calculate with precision
tax = PricingSettings.product_price * PricingSettings.tax_rate
```

#### UUID for Unique Identifiers

```python
from uuid import UUID

class ServiceSettings(CheapSettings):
    instance_id: UUID = UUID("00000000-0000-0000-0000-000000000000")

# Accepts multiple formats:
# INSTANCE_ID="550e8400-e29b-41d4-a716-446655440000"  # Standard
# INSTANCE_ID="550e8400e29b41d4a716446655440000"      # No hyphens
# INSTANCE_ID="{550e8400-e29b-41d4-a716-446655440000}" # With braces
```

### Environment Variable Naming

Environment variables are the uppercase version of the attribute name:

```python
class Settings(CheapSettings):
    database_url: str = "localhost"     # DATABASE_URL
    api_timeout: int = 30               # API_TIMEOUT
    enable_cache: bool = False          # ENABLE_CACHE
```

### Command Line Arguments

Command line arguments are the lowercase, hyphenated version of the attribute name:

```python
class Settings(CheapSettings):
    database_url: str = "localhost"     # --database-url
    api_timeout: int = 30               # --api-timeout
    enable_cache: bool = False          # --enable-cache / --no-enable-cache
```

#### Boolean Command Line Behavior

Boolean handling differs based on whether the type is Optional:

- **Non-Optional booleans** (`bool = False/True`) create both positive and negative flags:
  ```python
  class Settings(CheapSettings):
      debug: bool = False    # Creates both --debug and --no-debug
      secure: bool = True    # Creates both --secure and --no-secure
  ```
  This allows you to override environment variables in either direction:
  ```bash
  # Environment: DEBUG=true, SECURE=false
  python app.py --no-debug --secure  # Override both values
  ```

- **Optional booleans** (`Optional[bool]`) accept explicit values:
  ```python
  class Settings(CheapSettings):
      debug: Optional[bool] = None    # --debug true/false/1/0/yes/no
  ```

Both approaches allow overriding environment variables, but non-Optional booleans provide a cleaner flag-based interface.

### Inheritance

Settings classes support inheritance. Child classes inherit all settings from parent classes and can override them:

```python
class BaseSettings(CheapSettings):
    timeout: int = 30

class WebSettings(BaseSettings):
    timeout: int = 60  # Override parent
    port: int = 8080   # Add new setting
```

### Error Handling

- **Type conversion errors**: If an environment variable can't be converted to the expected type, a `ValueError` is raised with details
- **JSON parsing errors**: For `list` and `dict` types, JSON parsing errors include helpful messages
- **Missing attributes**: Accessing undefined settings raises `AttributeError`

### Performance

For performance-critical code where attribute access overhead matters, use `to_static()` to create a snapshot with no dynamic behavior:

```python
Settings = MyDynamicSettings.to_static()
# Now Settings.value is just a regular class attribute
```

### Environment-Only Settings

The `from_env()` method returns a class containing only settings that are explicitly set in environment variables:

```python
EnvOnly = MySettings.from_env()
# EnvOnly only has attributes for settings with environment variables
```

This is useful for debugging deployments or validating environment configuration.

### Settings Without Initializers

You can define settings with type annotations but no default values:

```python
class MySettings(CheapSettings):
    required_api_key: str  # No default value
    optional_timeout: Optional[int]  # No default, Optional type
```

By default, accessing uninitialized settings returns `None`:

```python
assert MySettings.required_api_key is None
assert MySettings.optional_timeout is None
```

Environment variables work normally with uninitialized settings:

```python
os.environ["REQUIRED_API_KEY"] = "secret123"
assert MySettings.required_api_key == "secret123"
```

For stricter validation, use `set_raise_on_uninitialized(True)` to make accessing uninitialized settings raise `AttributeError`:

```python
MySettings.set_raise_on_uninitialized(True)
MySettings.required_api_key  # Raises AttributeError if not in environment
```

**Note**: settings with `Optional` types (or unions with `None`), _never_ raise when uninitialized.
They always return `None` even if you `set_raise_on_uninitialized(True)`.

### Working with Credentials and .env Files

For sensitive settings like API keys or passwords, use `Optional` types with no default:

```python
class Settings(CheapSettings):
    api_key: Optional[str] = None
    db_password: Optional[str] = None
```

Since `cheap-settings` reads environment variables dynamically, it works seamlessly with `python-dotenv`:

```python
from dotenv import load_dotenv
from cheap_settings import CheapSettings

load_dotenv()  # Load .env file into environment
# Settings will automatically pick up the values
```
