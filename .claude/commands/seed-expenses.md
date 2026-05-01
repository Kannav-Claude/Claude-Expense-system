
Expense addition for the application
---
description: Seed realistic INR expense rows into expense_tracker.db for a given user across past months.
argument-hint: "<user_id> <count> <month>"
allowed-tools: Bash, Read
---
 
Seed expense data into the SQLite database at `instance/expense_tracker.db` using the arguments: $ARGUMENTS
 
Parse $ARGUMENTS as three positional values: `user_id`, `count`, `month`.
 
- `user_id` — integer; must match an existing `id` in the `users` table. Abort with a clear error if not found.
- `count` — integer; number of expense rows to insert **per category**. There are 7 categories (Food, Transport, Bills, Health, Entertainment, Shopping, Others), so total rows = count × 7.
- `month` — integer; how many past calendar months (including the current month) to spread expense dates across. E.g. `2` = current month + previous month.
## Steps
 
1. **Validate user** — run `SELECT id FROM users WHERE id = <user_id>` on the DB. If no row, print `Error: user_id <user_id> does not exist.` and stop.
2. **Resolve date window** — compute the first and last day of each of the `month` most-recent calendar months (including today's month) and build a pool of valid dates to sample from.
3. **Generate rows** — for each of the 7 categories produce `count` rows, each with:
   - A random `date` (YYYY-MM-DD) drawn from the date window.
   - A realistic `amount` (INR ₹, DECIMAL 10,2) within the range for that category:
     - Food → ₹300–₹800, Transport → ₹100–₹250, Bills → ₹800–₹3000
     - Health → ₹200–₹1500, Entertainment → ₹150–₹600
     - Shopping → ₹500–₹3000, Others → ₹50–₹300
   - A short human-sounding `description` fitting the category (e.g. "Monthly electricity bill", "Ola ride to airport", "Lunch at Saravana Bhavan").
4. **Insert** — use a single `executemany` INSERT into `expenses (user_id, amount, category, date, description)` inside a transaction. Print the number of rows inserted on success.
5. **Confirm** — run `SELECT category, COUNT(*), ROUND(SUM(amount), 2) FROM expenses WHERE user_id = <user_id> GROUP BY category ORDER BY category` and display the result as a summary table.