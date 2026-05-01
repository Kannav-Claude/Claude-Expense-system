# Expense Tracker Spec Command Structure

## Overview
The `/expense-tracker-spec` command is an interactive tool that generates detailed feature specification documents for the Expense Tracker application. It guides users through defining a new feature step-by-step and creates a comprehensive spec document for review before implementation.

## Command Invocation

```bash
/expense-tracker-spec
```

## Interactive Flow

### Step 1: Request Step Number
**Prompt:** "Enter the step number (e.g., 01, 02, 03, etc.):"
- User input: Two-digit number (01-99)
- Validation: Must be a valid number

### Step 2: Request Feature Name
**Prompt:** "Enter the feature name (e.g., Registration, Profile Page, Expense Management):"
- User input: Feature name as a string
- Validation: Cannot be empty

### Step 3: Processing
Once inputs are received, the command:
1. **Reads CLAUDE.md** - Extracts project context (tech stack, architecture, patterns, testing approach)
2. **Reads app.py** - Analyzes existing routes, structure, and Flask patterns
3. **Reads database/db.py** - Understands database layer and data models
4. **Analyzes project state** - Current directory structure and implementation patterns

### Step 4: Generate Spec Document
Creates a comprehensive spec with the following structure:

## Output Spec Document Structure

**File Name:** `[Step Number] [Feature Name].md`
**Location:** `.claude/commands/[Step Number] [Feature Name].md`

**Example:** `.claude/commands/01 Registration.md`

### Spec Document Sections

```markdown
# [Step Number]: [Feature Name]

## Overview
- Brief description of the feature
- Why it's important
- How it fits into the application

## Feature Requirements
- Primary objectives
- User interactions
- Expected outcomes

## Routes to Implement
- Route path
- HTTP method
- Request parameters (if any)
- Response structure
- Status codes

## Database Changes
- New tables (if any)
- Modified tables
- New columns
- Foreign key relationships
- Indexes needed

## Frontend Components
- New templates needed
- JavaScript functionality
- Form validation
- User feedback (alerts, messages)

## Testing Strategy
- Unit tests
- Integration tests
- Edge cases to cover
- Test data requirements

## Implementation Checklist
- [ ] Database schema created
- [ ] Routes implemented
- [ ] Templates created
- [ ] Frontend validation added
- [ ] Tests written
- [ ] Code reviewed
- [ ] Merged to main

## Clarifying Questions
(Section for asking the user about specific aspects of the feature)

## Dependencies
- Related features or steps
- External dependencies
- Blocking factors

## Notes
- Design decisions
- Considerations
- Known constraints
```

## Command Behavior Details

### File Reading & Analysis
- **CLAUDE.md**: Extract tech stack, patterns, testing approach, project structure
- **app.py**: Identify existing route patterns, Flask conventions used, current placeholders
- **database/db.py**: Understand database connection patterns, table structure, existing implementations

### Clarifying Questions
After generating the spec, the command should ask user-specific questions such as:
- "Which existing routes should be modified?"
- "Do we need to create new database tables or modify existing ones?"
- "What validations are required on the form?"
- "Should this feature be accessible to all users or only authenticated users?"
- "Are there any specific styling requirements?"

### Output Behavior
1. Generate the spec document with all sections filled based on existing code patterns
2. Display the spec to the user for review
3. Ask clarifying questions to refine the spec
4. Save the completed spec to `.claude/commands/[Step Number] [Feature Name].md`
5. **Do NOT start coding** - spec is for review only
6. Provide clear next steps for implementation

## Example Usage

```
User: /expense-tracker-spec

Command: Enter the step number (e.g., 01, 02, 03, etc.):
User: 03

Command: Enter the feature name (e.g., Registration, Profile Page):
User: Profile Page

[Command reads CLAUDE.md, app.py, db.py]

[Command generates detailed spec document]

Command: Here are some clarifying questions:
1. Should profile picture upload be included in this step?
2. Do you want users to edit their email address?
3. Should password change be on the profile page or separate?

[User answers questions]

[Spec is updated and saved to .claude/commands/03 Profile Page.md]

Command: Spec document created! Review the file and provide feedback before implementation begins.
```

## Key Principles

1. **No Code Generation** - Spec documents only, no implementation code
2. **Review First** - Users review and approve specs before coding starts
3. **Context-Aware** - Specs are generated based on actual project code and conventions
4. **Interactive** - Command asks clarifying questions to refine requirements
5. **Reusable** - Follows consistent structure across all features
6. **Comprehensive** - Covers routes, database, frontend, testing, and checklist

## Integration with Development Workflow

1. User runs `/expense-tracker-spec` with step number and feature name
2. Command generates detailed spec document
3. User reviews and approves spec (may request modifications)
4. User begins implementation based on approved spec
5. Implementation is guided by spec requirements and checklist
6. Tests are written following spec's testing strategy section
7. Code review references spec for completeness
