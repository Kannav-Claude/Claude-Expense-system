---
description: Seeds a single realistic dummy user into the expense tracking app's user table with duplicate email check.
allowed-tools: Read, Bash(python*)
---
You are seeding a single dummy user into the expense tracking application's user table.
 
## Task
 
Generate and insert **exactly 1 realistic dummy user** with the following fields:
- `name` — a realistic full name (first + last, mix of cultures/genders for variety)
- `email` — derived from the name, e.g. `john.smith@gmail.com` or `priya.mehta@outlook.com`
- `password` — a hashed password (use the same hashing method already used in this codebase)
---
 
## Steps to Follow
 
### 1. Understand the codebase
- Find the User model/schema (check `models/`, `prisma/schema.prisma`, `db/schema.rb`, `src/entities/`, or equivalent)
- Identify the exact column names for name, email, and password
- Find where existing seed files or DB scripts live (e.g. `prisma/seed.ts`, `db/seeds/`, `seeders/`, `scripts/`)
- Identify the hashing library already used (bcrypt, argon2, bcryptjs, etc.)
### 2. Check for duplicate email
Before inserting, **query the database to check if the generated email already exists**.
- If it exists, modify the email slightly (e.g. append a 2-digit number: `john.smith42@gmail.com`) and check again
- Never insert a user with a duplicate email
### 3. Generate the user
Pick a realistic name that hasn't been used recently. Good examples:
- `Sarah Okonkwo`, `Marcus Webb`, `Priya Nair`, `James Callahan`, `Mei-Lin Cho`, `Diego Fuentes`
Use a strong but simple dummy password like `Seed@2024!` — hash it before storing.
 
### 4. Insert the user
Use the existing DB client (Prisma, Sequelize, ActiveRecord, Knex, SQLAlchemy, etc.) — do NOT introduce a new library.
 
### 5. Confirm the result
After insertion, print:
```
✅ Seeded user created:
   Name:  <name>
   Email: <email>
   Password (plain): Seed@2024!
```
 
---
 
## Rules
- Create **only 1 user** per run — never batch insert
- Always hash the password — never store plain text
- Never modify existing users or other tables
- Use the project's existing DB connection and ORM — do not invent a new setup
- If the users table doesn't exist yet, say so and stop
 