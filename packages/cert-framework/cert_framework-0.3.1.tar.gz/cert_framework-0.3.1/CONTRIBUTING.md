# Contributing to CERT

Thank you for your interest in contributing to CERT! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Node.js 20+
- npm 10+
- Git
- Python 3.9+ (for Python bindings, optional)

### Getting Started

1. Fork and clone the repository:
```bash
git clone https://github.com/Javihaus/cert-framework.git
cd cert-framework
```

2. Install dependencies:
```bash
npm install
```

3. Build all packages:
```bash
npm run build
```

4. Run tests:
```bash
npm test
```

## Project Structure

```
cert-framework/
├── packages/
│   ├── core/              # Core testing primitives
│   ├── semantic/          # Semantic comparison engine
│   ├── inspector/         # Web UI (Next.js)
│   ├── cli/               # CLI tool
│   ├── langchain/         # LangChain integration
│   ├── python/            # Python bindings
│   └── pytest-plugin/     # pytest plugin
├── examples/              # Example implementations
├── docs/                  # Documentation
└── .github/               # CI/CD workflows
```

## Development Workflow

### Working on a Package

Each package is independently developed:

```bash
cd packages/core
npm run build    # Build TypeScript
npm test         # Run tests
npm run lint     # Type check
```

### Running in Watch Mode

For active development:

```bash
npm run dev  # Watches all packages in parallel
```

### Testing Changes

1. Make your changes in the appropriate package
2. Run tests: `npm test`
3. Build: `npm run build`
4. Test in the example: `cd examples/basic && npm test`

## Code Style

- TypeScript for core packages
- ESM modules (type: "module")
- Strict TypeScript configuration
- JSDoc comments for public APIs
- Descriptive variable names
- We use ruff for linting and formatting
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for public APIs

### Example:

```typescript
/**
 * Measures consistency by running a function N times.
 *
 * @param fn - Function to test
 * @param config - Test configuration
 * @returns Consistency measurement with evidence
 */
export async function measureConsistency<T>(
  fn: () => Promise<T>,
  config: TestConfig
): Promise<ConsistencyResult<T>> {
  // Implementation
}
```

## Adding Features

### Adding a New Comparison Rule

1. Add rule to `packages/semantic/src/comparator.ts`:
```typescript
export const myCustomRule: ComparisonRule = {
  name: 'my-custom-rule',
  priority: 85,
  match: (expected, actual) => {
    // Your matching logic
    return true; // or false, or 0-1 for confidence
  }
};
```

2. Register in SemanticComparator constructor
3. Add tests
4. Update documentation

### Adding a New CLI Command

1. Create command file in `packages/cli/src/commands/mycommand.ts`
2. Export command function
3. Register in `packages/cli/src/index.ts`
4. Update CLI documentation

## Testing

### Unit Tests

Use Vitest for unit tests:

```typescript
import { describe, it, expect } from 'vitest';
import { measureConsistency } from './consistency';

describe('measureConsistency', () => {
  it('returns 1.0 for identical outputs', async () => {
    const result = await measureConsistency(
      async () => '42',
      { nTrials: 5, consistencyThreshold: 0.85, ... }
    );
    expect(result.consistency).toBe(1.0);
  });
});
```

### Integration Tests

Test end-to-end workflows in `examples/`:

```bash
cd examples/basic
npm test
```

## Documentation

- Update README.md for major changes
- Add JSDoc comments to public APIs
- Create examples for new features
- Update CHANGELOG.md

## Commit Messages

Follow conventional commits:

```
feat: add gamma metric calculation
fix: correct consistency calculation for edge case
docs: update README with new examples
test: add tests for pipeline analyzer
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests
4. Update documentation
5. Run: `npm run build && npm test && npm run lint`
6. Commit with descriptive message
7. Push and create PR
8. Ensure CI passes

## Release Process

(For maintainers)

1. Update version in all package.json files
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`
5. GitHub Actions will publish to npm

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

