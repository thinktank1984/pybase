# Emmett Framework Documentation - Table of Contents

## Overview

Emmett is a Python web framework designed to be simple, fast, and full-featured. It combines the ease of Flask with powerful features from web2py, offering a complete toolkit for building modern web applications.

---

## Core Documentation

### Getting Started

#### **[Foreword](docs/foreword.md)**

#### **[Installation](docs/installation.md)**
Guide to installing Emmett using virtualenv on Python 3.9+. Covers setting up virtual environments, installing Emmett with pip, and preparing your development environment for both Python 3 systems.

#### **[Quickstart](docs/quickstart.md)**
Comprehensive quick-start guide covering: creating a Hello World application, routing with variable rules and HTTP methods, URL building, static files, the Renoir templating engine, JSON/XML services, the request object, pipelines for request processing, redirects and errors, sessions, forms, and internationalization. Perfect for understanding Emmett's core workflow.

#### **[Tutorial](docs/tutorial.md)**
Complete walkthrough of building "Bloggy," a micro-blogging application featuring user authentication, admin-only post creation, comments, and user registration. Covers application structure, database schema with ORM models, Auth module integration, migrations, route exposure, templates with inheritance, and basic styling. Demonstrates real-world patterns and best practices.

---

### Application Structure

#### **[Applications and Modules](docs/app_and_modules.md)**
Explains the `App` core class initialization parameters (import_name, root_path, url_prefix, template_folder, config_folder), application configuration using the config object and YAML files, application modules for organizing routes with shared prefixes/hostnames/pipelines, sub-modules for hierarchical organization, and module groups for exposing same routes with different pipelines.

#### **[Routing](docs/routing.md)**
Deep dive into Emmett's routing system using decorators. Covers: exposing functions with variable paths (int, float, str, date, alpha, any types), HTTP methods, template selection, output types (auto, bytes, str, template, snippet, iter, aiter, http), pipeline and injectors, exposing websockets, the URL helper for building URLs with parameters and anchors, handling static files with versioning, and routing multiple paths to the same function.

#### **[Patterns](docs/patterns.md)**
Best practices for structuring Emmett applications as they grow. Covers the package pattern (converting modules to packages for better organization), separating views into multiple files, organizing models and other components, and scaling from single-file apps to large, well-structured applications.

---

### Request and Response

#### **[Handling Requests](docs/request.md)**
Details the request object containing scheme, path, host, method, now (pendulum DateTime), headers, cookies, body, and client IP. Covers request variables (query_params, body, body_params, files), handling file uploads, and using awaitable attributes for async operations. Essential for understanding how to process incoming client requests.

#### **[Building Responses](docs/response.md)**
Explains the response object for customizing HTTP responses: status codes, cookies, headers, meta tags and meta properties for SEO. Covers wrapping methods for responding with iterables (wrap_iter, wrap_aiter), files (wrap_file), and IO streams (wrap_io). Includes examples of streaming responses and serving static files.

#### **[Pipeline](docs/pipeline.md)**
Comprehensive explanation of Emmett's request processing pipeline. Covers the Pipe class with open(), close(), pipe(), on_pipe_success(), and on_pipe_failure() methods, pipeline flow through bulkheads, the Injector class for injecting helpers into templates, error handling in pipes, and using pipes for authentication, logging, and cross-cutting concerns.

---

### Templates and Output

#### **[The Templating System](docs/templates.md)**
Complete guide to the Renoir templating engine. Covers: embedding Python code in HTML with {{ }} syntax, template structure with extend and include, blocks for inheritance, passing variables from controllers to templates, conditional rendering and loops, helper functions, custom helpers, and template snippets for inline rendering without files.

#### **[HTML without Templates](docs/html.md)**
Using the `tag` helper to generate HTML directly in Python code without templates. Covers: dynamically creating HTML elements, setting attributes with underscore notation, handling self-closing tags, auto-escaping content, using dictionaries for prefixed attributes (like HTMX), the `cat` helper for stacking elements, and building deep element hierarchies with context managers.

#### **[Services](docs/services.md)**
Exposing data in formats other than HTML. Covers: the service decorator (@service.json, @service.xml), ServicePipe for applying services to entire modules, JSON serialization, XML generation, and creating custom service formats for APIs and data exchange.

---

### Forms and Validation

#### **[Forms](docs/forms.md)**
Creating and handling forms with the Form class. Covers: defining forms with Field objects, validation and the accepted attribute, accessing submitted values via form.params, ModelForm for database-backed forms, editing records, form parameters (_action, _method, submit, csrf, keepvalues), handling file uploads with the upload parameter, customizing form styling with FormStyle, and onvalidation callbacks.

#### **[Validations](docs/validations.md)**
Built-in validation system for ensuring data quality. Covers: validation parameter syntax for Field and Model classes, presence and empty validators, format validators (email, URL, IP, JSON, date, time), length validators (min, max, range), numeric validators (gt, lt, gte, lte, between), inclusion validators (in, not_in), matching and exclusion validators, custom validation functions, and custom error messages.

---

### Database and ORM

#### **[Using Databases (ORM Overview)](docs/orm.md)**
Introduction to Emmett's integrated ORM based on pyDAL. Covers: supported database engines (SQLite, PostgreSQL, MySQL, MSSQL, MongoDB, and experimental engines), configuring database connections via app.config.db.uri, defining models with the Model class and Field objects, the Database pipe for request-scoped connections, basic queries using db(query).select(), and understanding the difference between Model classes and table instances.

#### **[Connecting](docs/orm/connecting.md)**
Database connection management and configuration. Covers: Database class initialization, connection lifecycle with the database pipe, manual connection management with connection(), connection_open(), and connection_close(), configuration via URI strings or separate parameters (adapter, host, user, password, database), connection pooling, and handling transactions in different contexts.

#### **[Models](docs/orm/models.md)**
Defining data models and table structure. Covers: Model class basics, table naming conventions and customization with tablename, Field types (string, text, blob, bool, int, float, decimal, date, time, datetime, password, upload, int_list, string_list, json, jsonb, geography, geometry), field validation, default values, update values, field visibility (readable/writable), form representations, indexes, and model-level validation rules.

#### **[Relations](docs/orm/relations.md)**
Defining relationships between models. Covers: belongs_to for required dependencies with cascade deletion, refers_to for optional references with nullify deletion, has_many for reverse one-to-many relations, has_one for reverse one-to-one relations, accessing related records as attributes, many-to-many relations via join tables, relation naming and customization, and querying related data efficiently.

#### **[Operations](docs/orm/operations.md)**
CRUD operations on database records. Covers: creating records with Model.create() and table.insert(), accessing created records, spatial field helpers for GIS data, selecting records with where(), counting, pagination, ordering, grouping, joining tables, updating records via set.update() or row.update_record(), deleting records with set.delete() or row.delete_record(), aggregation functions, raw SQL queries, and record serialization with as_dict().

#### **[Migrations](docs/orm/migrations.md)**
Database schema versioning and migrations. Covers: the migration engine using revision files, generating migrations with `emmett migrations generate`, migration file structure with up() and down() methods, applying migrations with `emmett migrations up`, reverting migrations with `emmett migrations down`, checking migration status with `emmett migrations status`, and handling schema changes (creating/dropping tables, adding/removing columns, altering column types).

#### **[Callbacks](docs/orm/callbacks.md)**
Hooks for executing code during database operations. Covers: before_insert for pre-insertion validation/modification, after_insert for post-insertion tasks, before_update for pre-update logic, after_update for post-update operations, before_delete for pre-deletion checks, after_delete for cleanup, callback return values (returning True aborts operations), and practical examples like creating related records or logging changes.

#### **[Scopes](docs/orm/scopes.md)**
Reusable query filters for models. Covers: the @scope decorator for defining named query shortcuts, using scopes on Model classes and Sets, combining scopes with other queries, scopes with arguments for dynamic filtering, default scopes that apply automatically to all queries, and practical examples for common filtering patterns (published posts, active users, date ranges).

#### **[Virtuals](docs/orm/virtuals.md)**
Computed and virtual attributes for models. Covers: computed fields with @compute decorator for storing calculated values in the database, the watch parameter for dependencies, virtual attributes with @rowattr decorator for runtime calculations without storage, @rowmethod decorator for methods available on selected rows, and when to use computed vs virtual attributes based on performance needs.

#### **[Advanced](docs/orm/advanced.md)**
Advanced ORM features and patterns. Covers: model inheritance and subclassing for shared fields/behaviors, extending base models without creating tables, overriding inherited properties, polymorphic tables, custom Table classes, direct pyDAL access for low-level operations, database-specific features, connection pooling configuration, and handling multiple databases in one application.

---

### Authentication and Security

#### **[Authorization System](docs/auth.md)**
Built-in authentication and authorization module. Covers: Auth class initialization with user model and database, AuthUser base model, exposed routes (login, logout, registration, profile, email verification, password recovery), Auth configuration (hmac_key, hmac_alg, password requirements, session expiration, registration verification), Auth module for routes, checking authentication with session.auth, managing groups and memberships, permission systems, requiring authentication with @requires decorator, and customizing auth templates.

---

### Sessions and State

#### **[Sessions](docs/sessions.md)**
Managing user session data across requests. Covers: session object for storing/retrieving user data, SessionManager.cookies for client-side cookie storage with encryption, SessionManager.files for server filesystem storage, SessionManager.redis for Redis-backed sessions, session configuration (expire time, secure flag, samesite, domain, cookie_name), compression levels, and choosing the right session backend for your needs.

---

### Communication

#### **[WebSockets](docs/websocket.md)**
Real-time bidirectional communication with WebSockets. Covers: the websocket object with scheme, path, host, headers, cookies, query_params, routing websockets with @app.websocket decorator, accepting connections with websocket.accept(), receiving messages with websocket.receive(), sending messages with websocket.send(), handling connection lifecycles, and building real-time features like chat or live updates.

---

### Internationalization

#### **[Languages](docs/languages.md)**
Multi-language support and internationalization. Covers: the T() translator object for marking translatable strings, storing translations in JSON/YAML files in the languages folder, file naming conventions (it.json, es.yaml), translation using HTTP Accept-Language headers vs. URL-based routing, setting default language with app.language_default, forcing URL-based language with app.language_force_on_url, language-specific URL generation, and organizing translations.

---

### Performance and Caching

#### **[Caching](docs/caching.md)**
Improving application performance with caching. Covers: Cache class initialization, RamCache handler for in-memory caching (fast but not shared between processes), DiskCache handler for filesystem-based caching (slower but persistent), RedisCache handler for Redis-backed caching (fast and shared), cache configuration (prefix, threshold, default_expire), cache decorators for memoization, manual cache operations (set, get, delete, clear), and designing effective caching strategies.

---

### Utilities and Tools

#### **[Mailer](docs/mailer.md)**
Sending emails from your application. Covers: Mailer class configuration with SMTP settings (server, port, username, password, TLS/SSL), creating messages with mailer.mail(), setting recipients, subject, body, and HTML content, adding attachments, sending messages immediately or creating for later, using templates for email bodies, and handling email delivery errors.

#### **[Extensions](docs/extensions.md)**
Extending Emmett with additional functionality. Covers: using extensions via app.use_extension(), extension configuration via app.config, accessing extension instances via app.ext, building custom extensions by subclassing Extension class, the on_load() lifecycle method, extension namespaces, using signals for communication, and publishing extensions as packages.

---

### Development and Debugging

#### **[Command Line Interface](docs/cli.md)**
Emmett's built-in CLI based on Click. Covers: the `emmett` command, automatic application discovery, specifying app with --app/-a flag, running development server with `emmett develop`, opening interactive shell with `emmett shell`, creating custom commands with @app.command decorator, command groups with @app.command_group, passing arguments to commands, and integrating with Click's rich CLI features.

#### **[Debug and Logging](docs/debug_and_logging.md)**
Debugging errors and logging application events. Covers: the built-in debugger for development showing application traceback, full traceback, and frame inspection, template error handling, logging configuration via app.config.logging, log levels (debug, info, warning, error, critical), using app.log for logging messages, rotating file handlers, log formatting, and production error tracking.

#### **[Testing](docs/testing.md)**
Testing Emmett applications with pytest or unittest. Covers: the test client with app.test_client(), making HTTP requests (get, post, put, patch, delete, head, options), inspecting responses via ClientResponse object, cookie handling between requests, following redirects, accessing application context (request, response, session, T) during tests, testing authentication flows, and writing effective test suites.

---

### Deployment

#### **[Deployment](docs/deployment.md)**
Running Emmett in production. Covers: the included Granian server with `emmett serve` command, server configuration options (host, port, workers, threads, blocking-threads, runtime-mode, interface, HTTP version, WebSocket support, loop implementation, logging, backlog, backpressure, SSL), using other ASGI servers (Uvicorn, Hypercorn, Daphne), Docker deployment with example Dockerfile, container orchestration considerations, and production best practices.

#### **[Upgrading](docs/upgrading.md)**
Migration guide for upgrading between Emmett versions. Covers: upgrading with pip, version-specific breaking changes and how to handle them, deprecated features and their replacements, new features in each version, and ensuring smooth upgrades with minimal code changes. Includes detailed migration instructions for major version changes.

---

## Additional Resources

### **[README](README.md)**
Quick introduction to Emmett framework with key features overview and links to full documentation.

### **[CHANGES](CHANGES.md)**
Complete version history and changelog detailing new features, bug fixes, breaking changes, and deprecations across all Emmett releases.

---

## Documentation Organization

This documentation is organized to guide you from basic concepts to advanced usage:

1. **Start with Getting Started** - Installation, Quickstart, and Tutorial
2. **Understand Core Concepts** - Applications, Routing, Request/Response, Pipeline
3. **Learn Data Management** - ORM, Models, Relations, Operations, Migrations
4. **Add Features** - Forms, Validation, Auth, Sessions, WebSockets
5. **Enhance and Deploy** - Caching, Testing, Debugging, Deployment

Each section builds upon previous concepts, but can also serve as a standalone reference for specific features.

