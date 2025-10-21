# Django ORM Language Server Protocol (LSP)

[![CI](https://github.com/JBSK8NC/django-lsp/actions/workflows/ci.yml/badge.svg)](https://github.com/JBSK8NC/django-lsp/actions/workflows/ci.yml)

A Language Server Protocol implementation for Django ORM that provides intelligent autocompletion for model queries, field lookups, and related field navigation.

## Features

- **Smart Completions**: Field lookups (`__exact`, `__contains`, `__startswith`) and related field navigation (`user__profile__bio`)
- **Context-Aware**: Only shows completions for imported models
- **Multi-App Support**: Works with Django projects that have multiple apps
- **Django Integration**: Uses Django's built-in field lookup APIs

## Installation

```bash
pip install django-qs-lsp
```

## Usage

### Running the Server

```bash
django-qs-lsp-server
```

### Neovim Setup

1. Install via Mason:
   ```vim
   :MasonInstall django-qs-lsp
   ```

2. Configure LSPConfig:
   ```lua
   require("lspconfig").django_lsp.setup({
     filetypes = { "python" },
     root_dir = require("lspconfig.util").root_pattern("manage.py"),
   })
   ```

## Supported Contexts

The LSP provides completions for:
- `Model.objects.filter(...)`
- `Model.objects.exclude(...)`
- `Model.objects.get(...)`
- `Model.objects.annotate(...)`
- `Model.objects.order_by(...)`

## Example

```python
from django.contrib.auth.models import User

# Field completions
User.objects.filter(username=  # Suggests: username=
User.objects.filter(email__   # Suggests: email__exact, email__contains, etc.

# Related field completions
User.objects.filter(profile__  # Suggests: profile__bio, profile__user, etc.
```

## Configuration

```bash
# Context-aware completions (default: true)
export DJANGO_LSP_CONTEXT_AWARE=true

# Debug logging
export DJANGO_LSP_DEBUG=true
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Code quality
ruff check .
mypy src/django_lsp/
```

## License

MIT License# Test release trigger
