# Contributing to Swarm-IOSM

Thank you for considering contributing to Swarm-IOSM! This document provides guidelines for contributions.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template
3. Provide:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Claude Code version and environment

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test with Claude Code
5. Commit with clear messages
6. Submit a Pull Request

## Development Guidelines

### Code Style

- Follow existing patterns in SKILL.md
- Use clear, descriptive names
- Document all templates with examples
- Keep markdown formatting consistent

### Templates

When adding or modifying templates:

1. Include clear section headers
2. Provide example content
3. Add cross-references to related templates
4. Update VALIDATION.md checklist

### Scripts

For Python scripts in `scripts/`:

1. Use type hints
2. Handle edge cases gracefully
3. Include usage examples in docstrings
4. Test with various plan structures

## Areas for Contribution

### High Priority

- **Gate Automation Scripts**: Scripts to measure IOSM gate criteria automatically
- **CI/CD Integration**: GitHub Actions, GitLab CI examples
- **Language-Specific Checkers**: Python, TypeScript, Rust gate evaluators

### Templates

- Additional subagent role templates
- Domain-specific PRD templates
- Custom iosm.yaml configurations

### Documentation

- More examples in `examples/`
- Video tutorials
- Integration guides for popular frameworks

### Integrations

- IDE plugins (VS Code, JetBrains)
- Issue tracker integrations
- Monitoring/observability tools

## Testing Your Changes

### Manual Testing

1. Install skill in a test project:
   ```bash
   cp -r .claude/skills/swarm-iosm /path/to/test-project/.claude/skills/
   ```

2. Run commands:
   ```
   /swarm setup
   /swarm new-track "Test feature"
   ```

3. Verify:
   - Skill activates correctly
   - Templates generate properly
   - Scripts run without errors

### Validation Script

```bash
python scripts/validate_plan.py swarm/tracks/<id>/plan.md
```

## Pull Request Process

1. **Title**: Use format `[component] Brief description`
   - Examples: `[templates] Add security review template`
   - Examples: `[scripts] Fix dependency graph cycle detection`

2. **Description**: Include:
   - What changes were made
   - Why they were needed
   - How they were tested

3. **Review**: PRs require one approval before merge

## Code of Conduct

- Be respectful and constructive
- Focus on the technical merits
- Welcome newcomers

## Questions?

- Open a GitHub issue with the `question` label
- Email: ecsiar@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve Swarm-IOSM!
