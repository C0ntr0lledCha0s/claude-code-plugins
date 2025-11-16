# Research Citation Guide

How to properly cite sources in research outputs for traceability and credibility.

## Why Citations Matter

Citations in research-agent outputs serve multiple purposes:
- **Traceability**: Track where information came from
- **Credibility**: Show evidence for claims
- **Reproducibility**: Others can verify findings
- **Attribution**: Give credit to original sources
- **Auditability**: Validate research quality

---

## Citation Types

### 1. Code File References

**Format**: `` `file-path:line-number` ``

Use backticks to make file references parsable by validation scripts.

**Examples**:
```markdown
The authentication logic is implemented in `src/auth/login.ts:42-88`.

The UserRepository defines the interface in `src/repositories/UserRepository.ts:15`.

Multiple database queries are executed in:
- `src/services/UserService.ts:105`
- `src/services/PaymentService.ts:67-92`
```

**Best Practices**:
- Include line numbers for precision
- Use line ranges for longer implementations (`42-88`)
- Always use relative paths from project root
- Validate file paths exist before submitting research

---

### 2. Web Resources

**Format**: `[descriptive text](URL)` + `[number]` citation marker

**Examples**:
```markdown
React Server Components are the default in Next.js 15 [1].

According to the official documentation [2], TypeScript 5.4 introduces
improved type inference for closures.

Sources:
[1] https://nextjs.org/docs/app/building-your-application/rendering/server-components
[2] https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-4.html
```

**Best Practices**:
- Use numbered citations like [1], [2]
- Include "Sources" or "References" section at end
- Prefer official documentation over blog posts
- Include access date for web sources that may change
- Link directly to relevant section (use URL anchors)

---

### 3. Package/Library Documentation

**Format**: Package name + version + documentation URL

**Examples**:
```markdown
## Dependencies

- **React** (v18.2.0) - [Official Docs](https://react.dev/)
- **Prisma** (v5.8.0) - [ORM Documentation](https://www.prisma.io/docs)
- **Express** (v4.18.2) - [API Reference](https://expressjs.com/en/4x/api.html)

The middleware pattern is documented in Express v4.x [3].

[3] Express.js Middleware - https://expressjs.com/en/guide/using-middleware.html
```

**Best Practices**:
- Always include version numbers
- Link to specific version docs when available
- Note if using different version than latest

---

### 4. Code Examples

**Format**: Code block + source citation

**Examples**:
```markdown
## Authentication Flow

The login handler follows this pattern:

\`\`\`typescript
// From src/auth/login.ts:42-58
async function handleLogin(credentials: Credentials) {
  const user = await validateCredentials(credentials);
  const token = await generateToken(user);
  return { user, token };
}
\`\`\`

Source: `src/auth/login.ts:42-58`
```

**Best Practices**:
- Always cite source after code blocks
- Indicate if code is simplified/modified
- Use comments to indicate source inline
- Don't include entire files - excerpt relevant parts

---

### 5. Design Patterns & Best Practices

**Format**: Pattern name + source/reference

**Examples**:
```markdown
## Patterns Identified

### Repository Pattern
The codebase uses the Repository pattern for data access [4].

Implementation: `src/repositories/UserRepository.ts:10-85`

Reference: [4] Martin Fowler - "Patterns of Enterprise Application Architecture"
https://martinfowler.com/eaaCatalog/repository.html
```

**Best Practices**:
- Cite pattern definition/explanation source
- Link to implementation in codebase
- Note any variations from standard pattern

---

### 6. Framework/Tool Documentation

**Format**: Tool name + documentation section + URL

**Examples**:
```markdown
## Build Configuration

The project uses Vite for building [5], configured in `vite.config.ts:1-35`.

Performance optimization is achieved through code splitting [6], as recommended
in the official Vite documentation.

References:
[5] Vite - Getting Started - https://vitejs.dev/guide/
[6] Vite - Features: Code Splitting - https://vitejs.dev/guide/features.html#code-splitting
```

---

### 7. Database Schema

**Format**: Schema file/migration + table/column reference

**Examples**:
```markdown
## Database Schema

Users are stored in the `users` table with the following structure:

- `id` (UUID, primary key)
- `email` (VARCHAR(255), unique)
- `password_hash` (VARCHAR(255))
- `created_at` (TIMESTAMP)

Schema: `prisma/schema.prisma:15-28`
Migration: `prisma/migrations/20250115_create_users/migration.sql`
```

---

### 8. API Endpoints

**Format**: HTTP method + path + implementation reference

**Examples**:
```markdown
## API Routes

### User Registration
`POST /api/users/register`

Handler: `src/routes/users.ts:42-67`
Validation: `src/validators/userSchema.ts:10-25`

### User Authentication
`POST /api/auth/login`

Handler: `src/routes/auth.ts:30-58`
```

---

## Complete Citation Example

Here's a complete research output with proper citations:

```markdown
# Investigation: Authentication System

## Summary

The application uses JWT-based authentication with refresh tokens.
Implementation follows security best practices [1] with HttpOnly cookies
and CSRF protection.

## Implementation Details

### Login Flow

1. User submits credentials to `POST /api/auth/login`
2. Credentials validated against database (`src/auth/validators.ts:15-35`)
3. JWT token generated with 15-minute expiry (`src/auth/jwt.ts:42`)
4. Refresh token created with 7-day expiry (`src/auth/jwt.ts:88`)
5. Tokens set as HttpOnly cookies

**Code Reference**:
```typescript
// Simplified from src/auth/login.ts:50-70
async function login(credentials: Credentials): Promise<AuthResult> {
  const user = await validateCredentials(credentials);
  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  setHttpOnlyCookie('accessToken', accessToken, { maxAge: 900 });
  setHttpOnlyCookie('refreshToken', refreshToken, { maxAge: 604800 });

  return { success: true, user };
}
```

Source: `src/auth/login.ts:50-70`

### Security Measures

The implementation includes several security features:

- **HttpOnly Cookies** - Prevents XSS attacks [2]
  - Implementation: `src/middleware/cookies.ts:25-40`

- **CSRF Protection** - Double-submit cookie pattern [3]
  - Implementation: `src/middleware/csrf.ts:15-88`

- **Token Rotation** - Refresh tokens rotated on use
  - Implementation: `src/auth/refresh.ts:42-67`

### Dependencies

- `jsonwebtoken` (v9.0.2) - JWT creation and verification [4]
- `bcrypt` (v5.1.1) - Password hashing [5]

## Best Practices Compliance

✓ Passwords hashed with bcrypt (OWASP recommendation) [6]
✓ Tokens expire (OWASP recommendation) [6]
✓ HttpOnly cookies prevent XSS [2]
✓ CSRF protection implemented [3]
✓ Secure session management [7]

## Recommendations

1. Consider implementing rate limiting on login endpoint [8]
2. Add account lockout after failed attempts [6]
3. Implement MFA for admin users [9]

## References

[1] JWT Best Practices - https://datatracker.ietf.org/doc/html/rfc8725
[2] OWASP - HttpOnly Cookie - https://owasp.org/www-community/HttpOnly
[3] OWASP - CSRF Prevention - https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
[4] jsonwebtoken npm - https://www.npmjs.com/package/jsonwebtoken
[5] bcrypt npm - https://www.npmjs.com/package/bcrypt
[6] OWASP Authentication Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
[7] OWASP Session Management - https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
[8] OWASP API Security - Rate Limiting - https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
[9] OWASP MFA Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html

## File References

All file paths are relative to project root:

- Authentication logic: `src/auth/login.ts:50-70`
- JWT utilities: `src/auth/jwt.ts`
- CSRF middleware: `src/middleware/csrf.ts:15-88`
- Cookie utilities: `src/middleware/cookies.ts:25-40`
- Validators: `src/auth/validators.ts:15-35`
```

---

## Citation Format Guidelines

### Numbering
- Use `[1]`, `[2]`, `[3]` for citations
- Number sequentially as they appear
- Place number after sentence or claim
- Group all references at end of document

### URLs
- Use full URLs, not shortened links
- Link to specific sections when possible (use `#anchors`)
- Prefer HTTPS
- Include version in URL if available (`/v5/docs/...`)

### File Paths
- Always relative from project root
- Use forward slashes (`/`)
- Include line numbers: `file.ts:42` or `file.ts:42-67`
- Use backticks to make parsable: `` `file.ts:42` ``

### Dates
For time-sensitive information:
```markdown
As of January 2025, React 18.2 is the stable version [1].

[1] React Versions (accessed 2025-01-15) - https://react.dev/versions
```

---

## Validation

Use the research-agent validation scripts to verify citations:

```bash
# Check that file references exist and line numbers are valid
python3 scripts/check-evidence.py research-output.md --codebase-dir /path/to/project

# Validate overall research quality including citations
python3 scripts/validate-research.py research-output.md
```

**Citation quality criteria**:
- [ ] All file references use backticks
- [ ] Line numbers provided for file references
- [ ] File paths are relative from project root
- [ ] URLs are complete and accessible
- [ ] Web sources include access date if time-sensitive
- [ ] All citation numbers are used
- [ ] References section is complete
- [ ] No broken links

---

## Quick Reference

### File Reference
```markdown
Implementation in `src/auth/login.ts:42-88`
```

### Web Citation
```markdown
According to the documentation [1], TypeScript improves type safety.

[1] TypeScript Handbook - https://www.typescriptlang.org/docs/handbook/intro.html
```

### Code Example with Citation
```markdown
\`\`\`typescript
// From src/utils/helper.ts:15-20
function validateEmail(email: string): boolean {
  return /^[^@]+@[^@]+$/.test(email);
}
\`\`\`

Source: `src/utils/helper.ts:15-20`
```

### Multiple Sources
```markdown
Security best practices recommend hashing passwords [1], using HTTPS [2],
and implementing CSRF protection [3].

[1] OWASP Password Storage - https://...
[2] OWASP Transport Layer Security - https://...
[3] OWASP CSRF Prevention - https://...
```

---

## Tools Integration

### With Validation Scripts
Citations in the format `` `file.ts:42` `` are automatically validated by:
- `check-evidence.py` - Verifies files exist and line numbers are valid
- `validate-research.py` - Checks for presence of citations

### With Link Checkers
Use standard markdown link format for URLs to enable link checking:
```bash
# Check for broken links
markdown-link-check research-output.md
```

---

## Common Mistakes

### ❌ Don't Do This

```markdown
// Vague reference - no line numbers
The code is in auth.ts somewhere

// No citation for claim
React is the best framework.

// Broken file reference format
See auth.ts line 42 (not parsable)

// Missing references section
Uses citation [1] but no [1] in references
```

### ✅ Do This

```markdown
// Precise file reference
Authentication logic: `src/auth/login.ts:42-88`

// Cited claim
React is widely adopted with 18M weekly npm downloads [1].

// Proper format
See `src/auth/login.ts:42` for implementation.

// Complete references
...uses JWT tokens [1].

[1] JWT Introduction - https://jwt.io/introduction
```

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
