---
date: 2025-01-15
topic: JWT tokens should use HttpOnly cookies, not localStorage
source: /best-practice JWT authentication
tags: [security, jwt, authentication, web, xss-prevention]
confidence: high
applied: false
reviewed_count: 0
last_reviewed: null
---

# What I Learned

## Key Insight
JWT tokens should be stored in HttpOnly cookies instead of localStorage to prevent XSS (Cross-Site Scripting) attacks.

## Why It Matters
- **Security vulnerability**: localStorage is accessible via JavaScript, making it vulnerable to XSS attacks
- **Attack surface**: If an attacker injects malicious JavaScript, they can steal tokens from localStorage
- **HttpOnly protection**: Cookies with the HttpOnly flag are inaccessible to JavaScript, preventing XSS token theft
- **Common mistake**: Many tutorials incorrectly recommend localStorage for simplicity

## How to Apply
```typescript
// ❌ INSECURE: Storing JWT in localStorage
localStorage.setItem('token', jwtToken);

// ✅ SECURE: Store JWT in HttpOnly cookie (server-side)
res.cookie('auth-token', jwtToken, {
  httpOnly: true,        // Prevents JavaScript access
  secure: true,          // HTTPS only
  sameSite: 'strict',    // CSRF protection
  maxAge: 15 * 60 * 1000 // 15 minutes
});

// Client-side: Cookie is automatically sent with requests
// No need to manually attach token to headers
fetch('/api/protected', {
  credentials: 'include'  // Include cookies in request
});
```

## Related Learnings
- CSRF protection is needed with cookie-based authentication (use CSRF tokens)
- Refresh token strategy for long sessions (separate refresh token cookie)
- Token expiration best practices (short-lived access tokens)
- Session vs. token-based authentication trade-offs

## Questions to Explore
- How to implement token refresh with HttpOnly cookies in Next.js?
- What about mobile apps where cookies might not work well?
- How to handle authentication in server-side rendered pages?
- Should refresh tokens also be HttpOnly cookies?

## Status Checklist
- [x] Understood concept
- [ ] Applied in code
- [ ] Reviewed and retained

## Notes
**OWASP Recommendation**: OWASP explicitly recommends HttpOnly cookies for JWT storage.

**Trade-offs**:
- Cookies add ~4KB to every request (header overhead)
- Need CSRF protection (unlike localStorage)
- Slightly more complex implementation
- But significantly more secure against XSS

**Migration path**:
If currently using localStorage, migrate by:
1. Implement server endpoint that sets HttpOnly cookie
2. Update client to use `credentials: 'include'`
3. Remove localStorage token handling
4. Add CSRF protection
