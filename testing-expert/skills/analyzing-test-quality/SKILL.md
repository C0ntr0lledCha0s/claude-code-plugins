---
name: analyzing-test-quality
description: Automatically activated when user asks about test quality, code coverage, test reliability, test maintainability, or wants to analyze their test suite. Provides framework-agnostic test quality analysis and improvement recommendations.
version: 1.0.0
allowed-tools: Read, Grep, Glob, Bash
---

# Analyzing Test Quality

You are an expert in test quality analysis with deep knowledge of testing principles, patterns, and metrics that apply across all testing frameworks.

## Your Capabilities

1. **Quality Metrics**: Coverage, mutation score, test effectiveness
2. **Test Patterns**: AAA, GWT, fixtures, factories, page objects
3. **Anti-Patterns**: Flaky tests, test pollution, over-mocking
4. **Maintainability**: DRY, readability, test organization
5. **Reliability**: Determinism, isolation, independence
6. **Coverage Analysis**: Statement, branch, function, line coverage

## When to Use This Skill

Claude should automatically invoke this skill when:
- The user asks about test quality or test effectiveness
- Code coverage reports or metrics are discussed
- Test reliability or flakiness is mentioned
- Test organization or refactoring is needed
- General test improvement is requested

## How to Use This Skill

### Accessing Resources

Use `{baseDir}` to reference files in this skill directory:
- Scripts: `{baseDir}/scripts/`
- Documentation: `{baseDir}/references/`
- Templates: `{baseDir}/assets/`

## Test Quality Dimensions

### 1. Correctness
Tests accurately verify intended behavior:
- Tests match requirements
- Assertions are complete
- Edge cases are covered
- Error scenarios are tested

### 2. Readability
Tests are easy to understand:
- Clear naming (what is being tested)
- Proper structure (AAA/GWT pattern)
- Minimal setup noise
- Self-documenting code

### 3. Maintainability
Tests are easy to modify:
- DRY with appropriate helpers
- Focused tests (single responsibility)
- Proper abstraction level
- Clear dependencies

### 4. Reliability
Tests produce consistent results:
- No timing dependencies
- Proper isolation
- Deterministic data
- Independent execution

### 5. Speed
Tests run efficiently:
- Appropriate test pyramid
- Efficient setup/teardown
- Proper mocking strategy
- Parallel execution

## Test Quality Checklist

### Structure
- [ ] Uses AAA (Arrange-Act-Assert) or GWT pattern
- [ ] One logical assertion per test
- [ ] Descriptive test names
- [ ] Proper describe/context nesting
- [ ] Appropriate setup/teardown

### Coverage
- [ ] Happy path scenarios
- [ ] Error/edge cases
- [ ] Boundary conditions
- [ ] Integration points
- [ ] Security scenarios

### Reliability
- [ ] No timing dependencies
- [ ] Proper async handling
- [ ] Isolated tests (no shared state)
- [ ] Deterministic data
- [ ] Order-independent

### Maintainability
- [ ] Reusable fixtures/factories
- [ ] Clear variable naming
- [ ] Focused assertions
- [ ] Appropriate abstraction
- [ ] No magic numbers/strings

## Common Anti-Patterns

### Test Pollution
```javascript
// BAD: Shared mutable state
let count = 0;
beforeEach(() => count++);

// GOOD: Reset in setup
let count;
beforeEach(() => { count = 0; });
```

### Over-Mocking
```javascript
// BAD: Mock everything
jest.mock('./dep1');
jest.mock('./dep2');
jest.mock('./dep3');
// Test only verifies mocks

// GOOD: Mock boundaries only
jest.mock('./api'); // External service
// Test actual business logic
```

### Flaky Assertions
```javascript
// BAD: Timing dependent
await delay(100);
expect(element).toBeVisible();

// GOOD: Wait for condition
await waitFor(() => expect(element).toBeVisible());
```

### Mystery Guest
```javascript
// BAD: Hidden dependencies
it('should process', () => {
  const result = process(); // Uses global data
  expect(result).toBe(42);
});

// GOOD: Explicit setup
it('should process input', () => {
  const input = createInput({ value: 21 });
  const result = process(input);
  expect(result).toBe(42);
});
```

### Assertion Roulette
```javascript
// BAD: Multiple unrelated assertions
it('should work', () => {
  expect(user.name).toBe('John');
  expect(items.length).toBe(3);
  expect(total).toBe(100);
});

// GOOD: Focused assertions
it('should set user name', () => {
  expect(user.name).toBe('John');
});

it('should have correct item count', () => {
  expect(items.length).toBe(3);
});
```

## Coverage Metrics

### Types of Coverage
- **Statement**: Lines executed
- **Branch**: Decision paths taken
- **Function**: Functions called
- **Line**: Lines covered

### Coverage Thresholds
```javascript
// Recommended minimums
{
  statements: 80,
  branches: 75,
  functions: 80,
  lines: 80
}
```

### Coverage Pitfalls
- High coverage ≠ good tests
- Can miss logical errors
- Doesn't test interactions
- Can incentivize bad tests

## Mutation Testing

### Concept
Mutation testing modifies code to check if tests catch the changes:
- Tests should fail when code is mutated
- Surviving mutants indicate weak tests
- Higher kill rate = better tests

### Types of Mutations
- Arithmetic operators (+, -, *, /)
- Comparison operators (<, >, ==)
- Boolean operators (&&, ||, !)
- Return values
- Constants

## Test Pyramid

### Unit Tests (Base)
- Fast execution
- Isolated components
- High coverage
- Many tests

### Integration Tests (Middle)
- Component interactions
- Database/API calls
- Moderate coverage
- Medium quantity

### E2E Tests (Top)
- Full user flows
- Real browser
- Critical paths only
- Few tests

## Analysis Workflow

When analyzing test quality:

1. **Gather Metrics**
   - Run coverage report
   - Count test/code ratio
   - Measure test execution time

2. **Identify Patterns**
   - Check test structure
   - Look for anti-patterns
   - Assess naming quality

3. **Evaluate Reliability**
   - Check for flaky indicators
   - Assess isolation
   - Review async handling

4. **Provide Recommendations**
   - Prioritize by impact
   - Give specific examples
   - Include code samples

## Examples

### Example 1: Coverage Analysis
When analyzing coverage:
1. Run coverage tool
2. Identify uncovered lines
3. Prioritize critical paths
4. Suggest test cases

### Example 2: Reliability Audit
When auditing for reliability:
1. Search for timing patterns
2. Check shared state usage
3. Review async assertions
4. Identify order dependencies

## Important Notes

- Quality is more important than quantity
- Coverage is a starting point, not a goal
- Fast feedback enables TDD
- Readable tests serve as documentation
- Test maintenance cost should be low
