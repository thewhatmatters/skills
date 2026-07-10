# Stage 3 · Verify decisions

A drafted `PRD.md` exists from Stage 2. Your job in this stage is to make
the user *actually read and own* every decision inside it before the spec
locks. Nothing gets built from an unverified spec.

The canonical instruction for this stage, verbatim from Karpathy's method:

> **"make me verify key decisions explicitly to ensure nothing is missed"**

## Why this stage exists

Every assumption an agent makes is a chance to drift. Karpathy's own list
of agent error patterns — silent assumptions, unresolved ambiguity,
unnecessary complexity, unauthorized edits beyond scope — are all things a
human catches at review time or pays for at build time. This stage is the
cheap moment to catch them. "You can outsource your thinking, but you
can't outsource your understanding."

## What to do

1. **Extract the list.** Re-read the drafted `PRD.md` and produce one
   explicit, numbered list containing:
   - every **assumption** you made while drafting (anything the user did
     not literally say in the interview);
   - every **key decision** the spec embeds (scope cuts, architecture and
     library choices, data shapes, sequencing, anything in Risks with a
     chosen mitigation);
   - every **ambiguity** you resolved silently — resolve it loudly here
     instead.
2. **Walk it item by item — via the AskUserQuestion tool.** Present each
   item as an AskUserQuestion: the question states the decision, the
   alternative(s) rejected, and why; the options are **Confirm** /
   **Change** / **Defer** (when the rejected alternatives are concrete,
   offer them as the Change options directly). Batch up to 4 themed items
   per tool call for speed — still one explicit answer per item, never a
   blanket approval. Fall back to plain text only if the tool is
   unavailable.
   - **Confirm** → mark it verified.
   - **Change** → edit `PRD.md` immediately, then re-confirm the edited
     item.
   - **Defer** → move it to the spec's Open questions section; a deferred
     decision is fine, an invisible one is not.
3. **No skipping.** Do not accept a blanket "looks good, approve all" on
   the first pass — the entire point is explicit verification. Offer the
   items individually at least once; if the user then insists on bulk
   approval, respect it, but record in the PRD's Open questions that
   verification was bulk-approved.
4. **Lock the spec.** When every item is confirmed, changed, or deferred,
   update `PRD.md` one final time and state plainly: the spec is reviewed
   and locked. Then continue to Stage 4 (author `CLAUDE.md` from the
   locked spec) — it is standard but declinable; the stage file explains
   how to offer it.

## Exit / resume contract

This stage is exit-able: the user can stop at any point and still hold a
usable artifact — the drafted `PRD.md`, plus the verification list with
its per-item status so far (append it under a `## Verification` heading
if pausing mid-review, and remove that heading when the review completes).
A later session resumes by continuing down the unconfirmed items instead
of regenerating the list. When this stage completes, the spec is locked
and the method continues to Stage 4 (`CLAUDE.md` from the locked PRD) —
declinable: a reviewed `PRD.md` alone remains a valid method outcome.
