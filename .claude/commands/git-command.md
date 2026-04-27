---
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*)
description: Safely stage and commit changes with confirmation, duplicate message checking, and no push.
---

# Git Commit

You are helping the user stage and commit changes. Follow these steps **exactly and in order**. Never run `git push` under any circumstances.

## Step 1 — Gather the commit message

Ask the user: **"What commit message would you like to use?"**

Use their answer to construct the commit message exactly as provided.

If the user passed arguments via `$ARGUMENTS`, use that as the commit message directly instead of asking.

---

## Step 2 — Check for duplicate commit messages

Run the following to check recent commit history:

```
git log --oneline -20
```

If a commit message **identical** to the one you are about to use already exists in the log, **stop and ask the user**:

> "A commit with the message `<message>` already exists in your recent history. Do you want to use a different message, or proceed anyway?"

Wait for their response before continuing.

---

## Step 3 — Show a pre-run confirmation

Show the user exactly what you are about to run:

```
git add .
git commit -m "<your commit message>"
```

Then ask: **"Shall I proceed with these two commands? (yes / no)"**

Do NOT run anything until the user confirms with "yes" or equivalent.

---

## Step 4 — Run the commands (only after confirmation)

Run in order:

1. `git add .`
2. `git commit -m "<message>"`

After each command, show the output to the user.

---

## Step 5 — Confirm completion

After both commands succeed, tell the user:

> "✅ Staged and committed. Nothing has been pushed to the remote repository."

---

## Hard rules

- **Never run `git push`** under any condition, even if the user asks mid-flow.
- If the user asks to push, respond: "This command is scoped to add + commit only. Run `git push origin <branch>` manually when you are ready."
- Always show the exact commands before executing them.
- Always check for duplicate commit messages before committing.
