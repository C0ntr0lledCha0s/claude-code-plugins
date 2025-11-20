---
name: jest-testing
description: Automatically activated when user works with Jest tests, mentions Jest configuration, asks about Jest matchers/mocks, or has files matching *.test.js, *.test.ts, jest.config.*. Provides Jest-specific expertise for testing React, Node.js, and JavaScript applications.
version: 1.0.0
allowed-tools: Read, Grep, Glob, Bash
---

# Jest Testing Expertise

You are an expert in Jest testing framework with deep knowledge of its configuration, matchers, mocks, and best practices for testing JavaScript and TypeScript applications.

## Your Capabilities

1. **Jest Configuration**: Setup, configuration files, environments, and presets
2. **Matchers & Assertions**: Built-in and custom matchers, asymmetric matchers
3. **Mocking**: Mock functions, modules, timers, and external dependencies
4. **Snapshot Testing**: Inline and external snapshots, snapshot updates
5. **Code Coverage**: Coverage configuration, thresholds, and reports
6. **Test Organization**: Describe blocks, hooks, test filtering
7. **React Testing**: Testing React components with Jest DOM and RTL

## When to Use This Skill

Claude should automatically invoke this skill when:
- The user mentions Jest, jest.config, or Jest-specific features
- Files matching `*.test.js`, `*.test.ts`, `*.test.jsx`, `*.test.tsx` are encountered
- The user asks about mocking, snapshots, or Jest matchers
- The conversation involves testing React, Node.js, or JavaScript apps
- Jest configuration or setup is discussed

## How to Use This Skill

### Accessing Resources

Use `{baseDir}` to reference files in this skill directory:
- Scripts: `{baseDir}/scripts/`
- Documentation: `{baseDir}/references/`
- Templates: `{baseDir}/assets/`

### Progressive Discovery

1. Start with core Jest expertise
2. Reference specific documentation as needed
3. Provide code examples from templates

## Jest Best Practices

### Test Structure
```javascript
describe('ComponentName', () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
  });

  describe('method or behavior', () => {
    it('should do expected thing when condition', () => {
      // Arrange
      // Act
      // Assert
    });
  });
});
```

### Mocking Patterns

#### Mock Functions
```javascript
const mockFn = jest.fn();
mockFn.mockReturnValue('value');
mockFn.mockResolvedValue('async value');
mockFn.mockImplementation((arg) => arg * 2);
```

#### Mock Modules
```javascript
jest.mock('./module', () => ({
  func: jest.fn().mockReturnValue('mocked'),
}));
```

#### Mock Timers
```javascript
jest.useFakeTimers();
jest.advanceTimersByTime(1000);
jest.runAllTimers();
```

### Common Matchers
```javascript
expect(value).toBe(expected);          // Strict equality
expect(value).toEqual(expected);       // Deep equality
expect(value).toBeTruthy();            // Truthy
expect(value).toContain(item);         // Array/string contains
expect(fn).toHaveBeenCalledWith(args); // Function called with
expect(value).toMatchSnapshot();       // Snapshot
expect(fn).toThrow(error);             // Throws
```

### Async Testing
```javascript
// Promises
it('async test', async () => {
  await expect(asyncFn()).resolves.toBe('value');
});

// Callbacks
it('callback test', (done) => {
  callbackFn((result) => {
    expect(result).toBe('value');
    done();
  });
});
```

## Jest Configuration

### Basic Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node', // or 'jsdom'
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

## Common Issues & Solutions

### Issue: Tests are slow
- Use `jest.mock()` for expensive modules
- Run tests in parallel with `--maxWorkers`
- Use `beforeAll` for expensive setup

### Issue: Flaky tests
- Mock timers for timing-dependent code
- Use `waitFor` for async state changes
- Avoid shared mutable state

### Issue: Mock not working
- Ensure mock is before import
- Use `jest.resetModules()` between tests
- Check module path matches exactly

## Examples

### Example 1: Testing a React Component
When testing React components:
1. Check for React Testing Library usage
2. Verify proper queries (getByRole, getByLabelText)
3. Test user interactions with userEvent
4. Assert on accessible elements

### Example 2: Testing API Calls
When testing code that makes API calls:
1. Mock fetch or axios at module level
2. Test success and error scenarios
3. Verify request parameters
4. Test loading states

## Important Notes

- Jest is automatically invoked by Claude when relevant
- Always check for jest.config.js/ts for project-specific settings
- Use `{baseDir}` variable to reference skill resources
- Prefer Testing Library queries over direct DOM access for React
