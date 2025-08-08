# Documentation Guidelines

## Documentation Structure and Organization

This project maintains a well-organized documentation structure in the `docs/` folder. When adding or updating documentation, you MUST follow the existing structure and enhance existing files rather than creating new ones unnecessarily.

## Existing Documentation Structure

```
docs/
├── README.md                           # Main documentation index
├── user/                              # End-user documentation
│   ├── INSTALLATION.md               # Installation instructions
│   ├── QUICKSTART.md                 # Quick start guide
│   └── USER_GUIDE.md                 # Comprehensive user guide
├── developer/                         # Developer documentation
│   ├── API.md                        # API documentation
│   ├── CONTRIBUTING.md               # Contribution guidelines
│   ├── DEVELOPER_GUIDE.md            # Developer setup and workflows
│   ├── STIX2_EXTENSIBILITY.md        # STIX2 extension documentation
│   └── TESTING.md                    # Testing guide and practices
└── deployment/                        # Deployment and operations
    ├── CONFIGURATION.md              # Configuration options
    ├── DEPLOYMENT.md                 # Deployment instructions
    ├── MONITORING.md                 # Monitoring and observability
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

## Documentation Guidelines

### 1. Always Check Existing Documentation First

Before creating new documentation files, you MUST:

1. **Check if relevant documentation already exists** in the appropriate category
2. **Read the existing content** to understand the current structure and style
3. **Enhance existing files** by adding new sections rather than creating new files
4. **Only create new files** if the content doesn't fit into any existing document

### 2. Documentation Categories and When to Use Them

#### User Documentation (`docs/user/`)
- **INSTALLATION.md**: Setup instructions, prerequisites, system requirements
- **QUICKSTART.md**: Getting started quickly, basic examples, first steps
- **USER_GUIDE.md**: Comprehensive usage instructions, all features, examples

**Add to existing user docs when:**
- Adding new installation methods or requirements
- Providing new quick start examples or workflows
- Documenting new user-facing features or tools

#### Developer Documentation (`docs/developer/`)
- **API.md**: API reference, endpoints, parameters, responses
- **CONTRIBUTING.md**: Contribution workflow, coding standards, PR process
- **DEVELOPER_GUIDE.md**: Development setup, architecture, code organization
- **STIX2_EXTENSIBILITY.md**: Framework extension guidelines
- **TESTING.md**: Testing practices, running tests, writing tests

**Add to existing developer docs when:**
- Adding new API endpoints or changing existing ones
- Updating development workflows or tooling
- Adding new testing practices or optimization techniques
- Documenting new architectural components or patterns

#### Deployment Documentation (`docs/deployment/`)
- **CONFIGURATION.md**: Configuration options, environment variables, settings
- **DEPLOYMENT.md**: Deployment procedures, environments, scaling
- **MONITORING.md**: Monitoring setup, metrics, alerting
- **TROUBLESHOOTING.md**: Common issues, debugging, solutions

**Add to existing deployment docs when:**
- Adding new configuration options or changing existing ones
- Documenting new deployment methods or environments
- Adding monitoring capabilities or metrics
- Documenting solutions to new issues or problems

### 3. Documentation Enhancement Rules

#### DO: Enhance Existing Files
```markdown
# Example: Adding to docs/developer/TESTING.md

## Existing Section
### Running Tests
[existing content]

## NEW: Add your content as a new section
### Test Execution Optimization
[your new optimization content]

## Existing Section Continues
### Test Categories
[existing content continues]
```

#### DON'T: Create Unnecessary New Files
```markdown
# ❌ DON'T create: docs/developer/TEST_OPTIMIZATION.md
# ✅ DO: Add to existing docs/developer/TESTING.md
```

### 4. Content Integration Guidelines

When adding content to existing documentation:

1. **Read the entire existing document** to understand the flow and structure
2. **Find the most appropriate section** to add your content
3. **Use consistent formatting** with the existing document style
4. **Update the table of contents** if the document has one
5. **Cross-reference related sections** within the same document or other docs
6. **Maintain the existing tone and style** of the document

### 5. Documentation Style Guidelines

#### Formatting Consistency
- Use the same heading levels as existing content
- Follow the same code block formatting (language tags, indentation)
- Use consistent bullet point styles (-, *, or numbered lists)
- Match the existing link formatting style

#### Content Organization
- **Logical flow**: New content should fit naturally into the document flow
- **Progressive complexity**: Start with simple concepts, build to advanced
- **Clear sections**: Use descriptive headings that match the document style
- **Examples and code**: Include practical examples that match existing patterns

#### Cross-References
- Link to related sections within the same document
- Reference other documentation files when relevant
- Use consistent link formatting: `[Text](path/to/file.md#section)`
- Update any existing cross-references that might be affected

### 6. When to Create New Documentation Files

Create new documentation files ONLY when:

1. **New major feature category** that doesn't fit existing structure
2. **Completely separate audience** not covered by user/developer/deployment
3. **Existing files would become too large** (>500 lines) with new content
4. **Content requires different format** (e.g., API reference vs. tutorial)

If creating new files:
- Follow the existing naming convention (UPPERCASE.md)
- Add the new file to the appropriate category folder
- Update the main docs/README.md to reference the new file
- Ensure the new file follows the same structure as existing files

### 7. Documentation Maintenance

When updating documentation:

1. **Check for outdated information** in the existing content
2. **Update version numbers** and compatibility information
3. **Verify all links and references** still work
4. **Test all code examples** and commands
5. **Update screenshots or diagrams** if they've changed

### 8. Examples of Good Documentation Integration

#### ✅ Good: Adding Test Optimization to TESTING.md
```markdown
# In docs/developer/TESTING.md

## Running Tests
[existing content]

### Optimized Test Execution  # NEW SECTION ADDED
The project includes several optimization features...
[new optimization content integrated naturally]

### Test Categories
[existing content continues]
```

#### ✅ Good: Adding New Configuration to CONFIGURATION.md
```markdown
# In docs/deployment/CONFIGURATION.md

## Environment Variables
[existing variables]

### Test Execution Configuration  # NEW SUBSECTION
# New environment variables for test optimization
PYTEST_XDIST_WORKER_COUNT=4
[new configuration options]

## Configuration Files
[existing content continues]
```

#### ❌ Bad: Creating Separate Files
```markdown
# ❌ Don't create: docs/developer/TEST_OPTIMIZATION.md
# ❌ Don't create: docs/deployment/TEST_CONFIG.md
# ✅ Instead: Add to existing TESTING.md and CONFIGURATION.md
```

## Implementation Checklist

When adding documentation, use this checklist:

- [ ] Checked if relevant documentation already exists
- [ ] Read existing documentation to understand structure and style
- [ ] Identified the most appropriate existing file for new content
- [ ] Added content as new sections/subsections in existing files
- [ ] Used consistent formatting and style with existing content
- [ ] Updated any table of contents or cross-references
- [ ] Verified all links and code examples work
- [ ] Only created new files if absolutely necessary
- [ ] Updated main docs/README.md if new files were created

## Documentation Review Process

Before finalizing documentation changes:

1. **Self-review**: Read through your additions in context of the full document
2. **Consistency check**: Ensure formatting and style match existing content
3. **Link verification**: Test all internal and external links
4. **Code testing**: Verify all code examples and commands work
5. **Flow check**: Ensure new content fits naturally into document flow

This approach ensures our documentation remains well-organized, comprehensive, and easy to navigate while avoiding unnecessary file proliferation.