# Bloggy - Micro-Blogging Application

A micro-blogging application built with the [Emmett](https://emmett.sh) web framework, demonstrating authentication, database operations, and web application patterns.

## Features

- **User Authentication**: Login, logout, and user registration
- **Admin System**: Admin-only post creation with group-based permissions
- **Blog Posts**: Create and view blog posts with timestamps
- **Comments**: Authenticated users can comment on posts
- **Database ORM**: Models with relationships and validation
- **Responsive UI**: Clean, simple interface

## Quick Start

### Prerequisites

- Python 3.9+ (Python 3.13+ recommended)
- uv package manager (will be installed if needed)

### Setup

Run the setup script from the project root:

```bash
# From the pybase root directory
./setup/setup_bloggy.sh
```

Or manually:

```bash
cd bloggy

# Create virtual environment
uv venv

# Install dependencies
uv pip install emmett>=2.5.0 pytest>=7.0.0

# Setup database and admin user
uv run emmett setup

# Run migrations (if needed)
uv run emmett migrations up
```

### Running the Application

```bash
# From project root
./run_bloggy.sh

# Or manually
cd bloggy
uv run emmett develop
```

The application will be available at: **http://localhost:8000/**

### Default Admin Credentials

- **Email**: `doc@emmettbrown.com`
- **Password**: `fluxcapacitor`

## Application Structure

```
bloggy/
├── app.py              # Main application file
├── tests.py            # Test suite
├── migrations/         # Database migrations
├── templates/          # HTML templates
│   ├── index.html     # Home page (post list)
│   ├── one.html       # Single post view with comments
│   ├── new_post.html  # Create new post (admin only)
│   ├── layout.html    # Base template
│   └── auth/          # Authentication templates
│       └── auth.html
└── static/             # Static files (CSS, JS, images)
    └── style.css
```

## Database Models

### User
Extends `AuthUser` from Emmett's auth system with relationships to posts and comments.

### Post
Blog posts with:
- Title and text content
- Timestamp
- Author (belongs to User)
- Comments (has many)

### Comment
Comments on posts with:
- Text content
- Timestamp
- Author (belongs to User)
- Associated post (belongs to Post)

## Routes

- `/` - Home page (list all posts)
- `/post/<id>` - View single post with comments
- `/new` - Create new post (admin only)
- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/register` - User registration

## Testing

Run the test suite:

```bash
# From project root (recommended - includes coverage by default)
./run_tests.sh

# With verbose output
./run_tests.sh -v

# Without coverage report
./run_tests.sh --no-coverage

# Or manually from bloggy directory
cd bloggy
uv run pytest tests.py -v

# With coverage
uv run pytest tests.py --cov=app
```

Tests include:
- Empty database state
- User authentication
- Admin access control
- Post creation and viewing
- Comment functionality

## Development Commands

```bash
# Start development server
uv run emmett develop

# Run tests
uv run pytest tests.py

# Run tests with coverage
uv run pytest tests.py --cov=app

# Generate new migration
uv run emmett migrations generate

# Apply migrations
uv run emmett migrations up

# Revert migrations
uv run emmett migrations down

# Setup admin user (run once)
uv run emmett setup

# Open interactive shell
uv run emmett shell
```

## Key Concepts Demonstrated

### Authentication & Authorization
- Email-based authentication using Emmett's Auth module
- Group-based permissions (admin group)
- Route protection with `@requires` decorator
- Session management

### ORM Patterns
- Model definition with fields and validation
- Relationships: `belongs_to`, `has_many`
- Default values and field visibility
- Database operations (CRUD)

### Request Pipeline
- Session management with cookies
- Database connection per request
- Authentication pipeline

### Form Handling
- Model-based forms with validation
- CSRF protection
- Custom form callbacks (`onvalidation`)
- Form parameters and submission

### Template Rendering
- Template inheritance with extend/include
- Passing data from routes to templates
- Conditional rendering based on auth state
- URL generation with `url()` helper

## Architecture Notes

This application follows Emmett framework patterns:

1. **Models** define database structure with validation
2. **Routes** expose HTTP endpoints with decorators
3. **Pipeline** processes requests through middleware
4. **Templates** render HTML with Python-like syntax
5. **Forms** handle user input with validation

## Related Documentation

- **Emmett Framework**: See `/emmett_documentation/` in the project root
- **Tutorial**: `/emmett_documentation/docs/tutorial.md`
- **ORM Guide**: `/emmett_documentation/docs/orm/`
- **Auth System**: `/emmett_documentation/docs/auth.md`

## Comparison with DjangoBase

While DjangoBase (in `/djangobase/`) is a full-featured Django application, Bloggy demonstrates:
- Simpler, more direct patterns
- Less boilerplate code
- Integrated ORM and auth
- Single-file application structure

Both frameworks offer similar capabilities but with different architectural approaches.

## Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm -f *.db
uv run emmett setup
```

### Migration Problems
```bash
# Check migration status
uv run emmett migrations status

# Generate fresh migration
uv run emmett migrations generate

# Apply migrations
uv run emmett migrations up
```

### Port Already in Use
```bash
# Use a different port
uv run emmett develop --port 8001
```

## License

This example application is provided for educational purposes as part of the pybase project.

## Learn More

- [Emmett Framework Documentation](https://emmett.sh/docs)
- [Emmett GitHub](https://github.com/emmett-framework/emmett)
- Full Emmett docs in this project: `/emmett_documentation/`

