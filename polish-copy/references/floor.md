# The floor — voice-independent microcopy craft

Loaded by `SKILL.md` Step 4 on every pass. These rules hold regardless of
brand voice; a violation is 🟠 (or 🔴 when the copy misleads or blocks).

## 1. Buttons & CTAs

- **Verb + object, specific to the action.** "Save changes", "Create project",
  "Send invite" — never bare "Submit", "OK", "Yes", "Continue" on anything
  consequential. The button label should answer "what happens when I press this".
- **Destructive confirms name the stakes.** "Delete 3 projects" / "Delete" +
  "Keep them" — never "Are you sure?" + OK/Cancel. 🔴 when the destructive
  choice is the visually-primary or ambiguous one.
- **Sibling buttons agree** in form (all verb-first), casing, and tense.

## 2. Errors

- **Say what happened + what to do next**, in the user's terms. "That email is
  already registered — try signing in instead" beats "Invalid input" /
  "Error 422" / "Something went wrong" (the last is acceptable only for truly
  unknown failures, and still needs a next step: retry, status link, support).
- **Never blame the user** ("you entered an invalid…") — describe the mismatch.
- **No leaked internals**: status codes, exception names, field keys
  (`user_email_idx violation`) in user-facing text is 🔴.

## 3. Empty states

- An empty state is an onboarding surface, not a shrug. "No results" alone is
  a violation; pair *why it's empty* with *the one action that fills it*
  ("No projects yet — create your first one").
- First-run vs filtered-to-empty are different states; copy that conflates
  them ("No results found" on a brand-new account) is 🟠.

## 4. Placeholders & labels

- **Placeholder ≠ label.** A placeholder that carries the only naming of the
  field is 🟠 (and an a11y finding — cross-reference audit-ui). Placeholders
  show *format examples* ("you@company.com"), not instructions.
- Labels are nouns, short, and match the user's vocabulary, not the schema's
  (`display_name` → "Name").

## 5. Consistency (sweep-level, not per-string)

- **One casing policy** for each surface class — buttons, menu items, headings —
  applied everywhere (sentence case vs Title Case; either is fine, mixing isn't).
- **One tense/person** throughout ("Manage your team" vs "Manage my team").
- **One term per concept** — "workspace" on one screen and "team space" on
  another is 🟠 even when both read fine alone.
- Punctuation policy: tooltips/helpers either all end with periods or none do.

## 6. Jargon & register

- System vocabulary out of UI: "session expired" → "You've been signed out";
  "null", "undefined", "N/A" in rendered output is 🔴.
- Abbreviations only when the audience owns them.

## 7. Notifications, toasts, loading

- Success toasts confirm the *result*, not the mechanism ("Invite sent" not
  "POST successful"); skip toasts for instantly-visible results.
- Loading states name the work when it's slow ("Generating report…") — bare
  spinners over 2s with no words is 🟡.

## 8. Tooltips & helper text

- A tooltip that restates the label ("Settings — open settings") is 🟡 noise:
  cut it or make it add something (shortcut, consequence, limit).
- Helper text answers the question the field actually raises (format? why
  needed? who sees it?).
