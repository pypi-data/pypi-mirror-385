# FastApps v1.0.8 - PyPI Release Notes

## 🎉 Published Successfully!

**Package**: fastapps  
**Version**: 1.0.8  
**PyPI URL**: https://pypi.org/project/fastapps/1.0.8/  
**Release Date**: January 17, 2025

---

## 📦 What's New in v1.0.8

### Major Feature: Complete OAuth 2.1 Authentication System

FastApps now includes a production-ready OAuth 2.1 authentication system that makes securing your ChatGPT widgets incredibly simple.

#### 1. Server-Wide Authentication (3 Parameters)

Enable OAuth for all widgets with just 3 parameters:

```python
from fastapps import WidgetMCPServer

server = WidgetMCPServer(
    name="my-widgets",
    widgets=tools,
    auth_issuer_url="https://tenant.auth0.com",
    auth_resource_server_url="https://example.com/mcp",
    auth_required_scopes=["user"],
)
```

Features:
- ✅ Built-in JWT verification with JWKS auto-discovery
- ✅ Supports Auth0, Okta, Azure AD, AWS Cognito
- ✅ Custom `TokenVerifier` for advanced cases
- ✅ Automatic token validation on every request

#### 2. Per-Widget Authentication Decorators

Control auth requirements per widget:

```python
from fastapps import BaseWidget, auth_required, no_auth, optional_auth, UserContext

# Require authentication
@auth_required(scopes=["user", "write:data"])
class ProtectedWidget(BaseWidget):
    async def execute(self, input_data, context, user: UserContext):
        return {"user_id": user.subject, "scopes": user.scopes}

# Explicitly public
@no_auth
class PublicWidget(BaseWidget):
    async def execute(self, input_data, context, user):
        return {"message": "Public content"}

# Optional authentication (freemium)
@optional_auth(scopes=["user"])
class FlexibleWidget(BaseWidget):
    async def execute(self, input_data, context, user: UserContext):
        if user.is_authenticated:
            return {"tier": "premium", "user": user.subject}
        return {"tier": "free"}
```

#### 3. Enhanced CLI Commands

Create authenticated widgets instantly:

```bash
# Protected widget
fastapps create admin --auth --scopes admin,write:data

# Public widget
fastapps create search --public

# Optional auth widget
fastapps create content --optional-auth --scopes user

# Get auth help
fastapps auth-info
```

Features:
- ✅ Auto-generates decorators and imports
- ✅ Creates auth-aware execute() methods
- ✅ Shows auth status in terminal output
- ✅ Quick reference command (`auth-info`)

#### 4. UserContext for Authenticated Users

Access user information in your widgets:

```python
async def execute(self, input_data, context, user: UserContext):
    # Properties
    user.is_authenticated  # bool
    user.subject           # User ID
    user.client_id         # OAuth client
    user.scopes            # List of scopes
    user.claims            # Full JWT claims
    
    # Methods
    user.has_scope("admin")  # Check scope
```

---

## 🔐 Security Features

- **RS256 JWT Validation**: Secure signature verification
- **JWKS Auto-Discovery**: Automatic public key fetching
- **Scope Enforcement**: Fine-grained permission control
- **Server-Side Enforcement**: Can't be bypassed by client
- **MCP Specification Compliant**: Follows official patterns

---

## 📚 New Documentation

- **docs/08-AUTH.md** (11.8KB) - Server-wide OAuth setup
- **docs/09-PER-WIDGET-AUTH.md** (15KB) - Per-widget decorators
- **OAUTH_TESTING_GUIDE.md** - Complete Auth0 testing guide
- **CLI_COMMANDS_UPDATED.md** - Updated CLI reference
- **CLI_EXAMPLES.md** - Real-world CLI examples

---

## 🆕 New Exports

```python
from fastapps import (
    # New in v1.0.8
    JWTVerifier,        # Built-in JWT verifier
    TokenVerifier,      # Base class for custom verifiers
    AccessToken,        # Token data class
    UserContext,        # Authenticated user context
    auth_required,      # Auth required decorator
    no_auth,            # Public widget decorator
    optional_auth,      # Optional auth decorator
    
    # Existing
    BaseWidget,
    ClientContext,
    WidgetMCPServer,
    Field,
    ConfigDict,
)
```

---

## 📦 New Dependencies

- `PyJWT>=2.8.0` - JWT token validation
- `cryptography>=41.0.0` - RS256 signature verification
- `httpx>=0.28.0` - HTTP client for JWKS

---

## 🔄 Upgrade Guide

### From v1.0.7 or earlier

```bash
pip install --upgrade fastapps
```

**Backward Compatibility:** All existing code continues to work. Auth is optional.

**To use auth features:**

1. **Server-wide auth** - Add parameters to `WidgetMCPServer`
2. **Per-widget auth** - Use decorators on widgets
3. **CLI shortcuts** - Use `--auth`, `--public`, `--optional-auth` flags

---

## 🚀 Quick Start with Auth

```bash
# Install
pip install fastapps==1.0.8

# Create project
fastapps init my-app
cd my-app
pip install -r requirements.txt && npm install

# Create authenticated widget
fastapps create admin --auth --scopes admin

# Configure OAuth in server/main.py
# Build and run
npm run build
python server/main.py
```

---

## 📊 Package Statistics

- **Version**: 1.0.8
- **Python**: 3.11+
- **Wheel Size**: 41.5 KB
- **Source Size**: 106.1 KB
- **Files**: 21 Python modules
- **Documentation**: 50+ KB

---

## 🎯 What's Included

### Core Modules
- `fastapps/core/widget.py` - BaseWidget, UserContext, ClientContext
- `fastapps/core/server.py` - WidgetMCPServer with OAuth
- `fastapps/builder/compiler.py` - Widget builder

### Auth Modules (NEW)
- `fastapps/auth/verifier.py` - JWTVerifier
- `fastapps/auth/decorators.py` - Auth decorators
- `fastapps/auth/__init__.py` - Auth exports

### CLI Modules
- `fastapps/cli/main.py` - CLI with auth commands
- `fastapps/cli/commands/create.py` - Smart widget generation
- `fastapps/cli/commands/init.py` - Project scaffolding

---

## 🔍 Installation Verification

After installing, verify auth features:

```python
from fastapps import (
    BaseWidget,
    UserContext,
    auth_required,
    no_auth,
    optional_auth,
    JWTVerifier,
)

print("✓ All auth features available!")
```

Or check CLI:

```bash
fastapps --version  # Should show 1.0.8
fastapps auth-info  # Should display auth guide
```

---

## 📖 Documentation Links

- **PyPI Page**: https://pypi.org/project/fastapps/1.0.8/
- **GitHub**: https://github.com/fastapps-framework/fastapps
- **Documentation**: https://fastapps.dev/docs
- **Server Auth Guide**: docs/08-AUTH.md
- **Widget Auth Guide**: docs/09-PER-WIDGET-AUTH.md

---

## 🐛 Bug Fixes

None - this is a feature release.

---

## ⚠️ Breaking Changes

None - fully backward compatible with v1.0.7 and earlier.

---

## 🎓 Next Steps for Users

1. **Upgrade**: `pip install --upgrade fastapps`
2. **Read docs**: Check `docs/08-AUTH.md` for setup
3. **Set up OAuth**: Create Auth0 or Okta tenant
4. **Test**: Use `OAUTH_TESTING_GUIDE.md` for testing
5. **Deploy**: Secure your widgets!

---

## 👥 Contributors

FastApps Team

---

## 📝 Changelog

### v1.0.8 (2025-01-17)

**Added:**
- Server-wide OAuth 2.1 authentication
- Built-in JWTVerifier with JWKS auto-discovery
- Per-widget auth decorators (@auth_required, @no_auth, @optional_auth)
- UserContext for accessing authenticated user info
- CLI flags for widget creation with auth (--auth, --public, --optional-auth, --scopes)
- New CLI command: `fastapps auth-info`
- Comprehensive authentication documentation (26KB+)
- OAuth testing guide and automation scripts
- PyJWT, cryptography dependencies

**Changed:**
- WidgetMCPServer accepts OAuth parameters
- BaseWidget.execute() signature includes `user` parameter
- CLI create command generates auth-aware code
- Version bumped to 1.0.8

**Fixed:**
- None

---

## 🎉 Summary

FastApps v1.0.8 delivers **complete OAuth 2.1 authentication** with:
- ✅ 3-parameter server configuration
- ✅ Per-widget control with decorators
- ✅ Built-in JWT verification
- ✅ CLI shortcuts for fast development
- ✅ MCP specification compliant
- ✅ Production ready
- ✅ Fully documented

Install now:
```bash
pip install fastapps==1.0.8
```

---

**License**: MIT  
**Support**: https://github.com/fastapps-framework/fastapps/issues

