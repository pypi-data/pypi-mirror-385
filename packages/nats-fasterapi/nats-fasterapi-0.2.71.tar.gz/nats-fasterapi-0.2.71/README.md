# ⚡ FasterAPI — Scaffold FastAPI Apps with Ease

`nats-fasterapi` is a **CLI tool** that helps you scaffold and supercharge FastAPI projects.  

It generates schemas, CRUD repositories, services, routes, and authentication utilities — so you can focus on building features instead of repetitive boilerplate. Think of it as a **FastAPI project generator + productivity booster 🚀**.  


## ✨ Features

- 🏗️ Generate **Pydantic schemas** with a single command.  
- 🗄️ Generate **CRUD repositories** backed by MongoDB (`motor`), Redis, or custom logic.  
- 🔧 Generate **service layers** to connect repositories and routes.  
- 🌐 Generate **API routes** with versioning support (`latest-modified` / `highest-number`).  
- 🔑 Generate **token-based authentication utilities** (repository + dependencies).  
- ⚡ **Mount routes automatically** into `main.py`.  
- 🎯 Interactive prompts or automation-friendly `-y` (yes) flag.  
- 📦 Designed for **scalable microservices** using FastAPI.  

---

## 📦 Installation

```bash
pip install nats-fasterapi
````

Upgrade to the latest version anytime:

```bash
fasterapi update
```

---

## 🚀 Usage

Run `fasterapi --help` to see all available commands:

```
Usage: fasterapi [OPTIONS] COMMAND [ARGS]...

  ⚡ FasterAPI CLI — Scaffold and supercharge your FastAPI projects

Options:
  -v, --version  Show the FasterAPI version and exit
  --help         Show this message and exit

Commands:
  make-crud       Generate CRUD repository functions
  make-schema     Generate Pydantic schemas
  make-service    Generate service layer templates
  make-route      Generate route files (with versioning)
  make-token-repo Generate token repository for roles
  make-token-deps Generate token dependency utilities
  mount           Mount routes into main.py
  run-d           Run the dev server (uvicorn --reload)
  update          Upgrade FasterAPI CLI to latest
```

---

## 🛠️ Commands Overview

### `make-schema`

Generate a Pydantic schema.

```bash
fasterapi make-schema user
```

✅ Good:

```bash
fasterapi make-schema product
```

❌ Bad:

```bash
fasterapi make-schema User   # Avoid uppercase
fasterapi make-schema        # Missing name
```

---

### `make-crud`

Generate CRUD repository functions for a schema.

```bash
fasterapi make-crud user
```

---

### `make-service`

Generate a service layer for a schema.

```bash
fasterapi make-service user
```

---

### `make-route`

Generate an API route with a versioning strategy.

```bash
fasterapi make-route user --version-mode latest-modified
fasterapi make-route product --version-mode highest-number
fasterapi make-route order      # Will ask interactively
fasterapi make-route order -y   # Skips prompt, defaults to highest-number
```

---

### `make-token-repo`

Generate a token repository for authentication.

```bash
fasterapi make-token-repo admin user staff
```

If no roles are provided, it defaults to:

```
admin, user, staff, guest-editor
```

---

### `make-token-deps`

Generate token dependency utilities.

```bash
fasterapi make-token-deps
```

---

### `mount`

Mount all API routes into `main.py`.

```bash
fasterapi mount
```

---

### `run-d`

Run the development server with uvicorn.

```bash
fasterapi run-d
```

Equivalent to:

```bash
uvicorn main:app --reload
```

---

### `update`

Upgrade FasterAPI CLI to the latest version.

```bash
fasterapi update
```

---

## 👨‍💻 Development

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/yourusername/nats-fasterapi.git
cd nats-fasterapi
pip install -e .
```

Run tests:

```bash
pytest
```

---

## 🛣️ Roadmap

Here’s what’s coming next for FasterAPI 🚀:

### Database Support

* [ ] SQLAlchemy (PostgreSQL / MySQL) repository generator
* [ ] SQLite lightweight repository scaffolding
* [ ] Cassandra & DynamoDB templates
* [ ] Neo4j graph database integration

### Global Config Support

* [ ] Central config file (`fasterapi.yaml`) to scaffold schema, repo, service, and routes automatically
* [ ] Environment-specific overrides for config-driven scaffolding

### Authentication Enhancements

* [ ] Social logins (Google, GitHub, Facebook, Twitter) with OAuth2
* [ ] JWT refresh token rotation utilities
* [ ] API key and HMAC authentication scaffolding

### Project Scaffolding

* [ ] `fasterapi new myproject` to bootstrap a full FastAPI project
* [ ] Opinionated folder structure with best practices baked in

### DX (Developer Experience) Improvements

* [ ] Global `--yes` flag (applies to all commands for CI/CD)
* [ ] Configurable templates for schema, CRUD, services, routes
* [ ] Built-in Dockerfile & `docker-compose` scaffolding
* [ ] Built-in GitHub Actions CI/CD workflow generator

### Other Ideas

* [ ] CLI autocompletion for bash/zsh/fish
* [ ] Schema-first API generator (OpenAPI → code scaffolding)
* [ ] Hot reload template customization

---

## 📄 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

© 2025 Nathaniel Uriri

```
```
