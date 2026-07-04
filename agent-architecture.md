# Agent Architecture — Canonical Spec

The single source of truth for how a subagent in this family is built —
the definitions in `~/.claude/agents/*.md` that the Agent tool spawns as
fan-out workers. Companion to `skill-architecture.md`: **skills encode
procedure (the how); agents are thin domain wrappers — identity +
constraints + knowledge + output contract — that delegate procedure to
skills.** A future `generate-agent` scaffolds to this (deferred until the
agent population outgrows hand-authoring, ~5+); the weekly
`vault-skills-lint` launchd job already lints every agent's frontmatter.

Reference implementations: `vault-verifier`, `skill-auditor`.
Last updated: 2026-07-03 (initial version, distilled from the first
suite-wide fan-out run and its incidents).

---

## G. Architecture patterns

A conforming agent SHOULD embody these. Deviations should be deliberate and
recorded in the definition itself (agents have no handoff.md — the file is
the whole artifact).

1. **One flat file, strict YAML.** `~/.claude/agents/<name>.md`;
   frontmatter `name` matches the filename stem; frontmatter parses under
   `yaml.safe_load`, not just the harness's lenient reader (`>-`-fold any
   description containing `: `). A persona doc in a subdirectory is not an
   agent — it never loads.
2. **Description written for the router.** The `description` is what the
   coordinating model reads when deciding to spawn: say when to use it, the
   unit of work it takes (one article, one skill dir), what it returns, and
   what it never does. Like skill descriptions it is always-loaded context —
   trigger-rich but lean.
3. **Domain-scoped, smallest viable surface.** One domain, the smallest
   `tools:` allowlist that does the job, the smallest task grain that
   parallelizes (one target per spawn; the coordinator merges). Composition
   over inheritance: prefer another small agent over a fatter one.
4. **Constraints enforced in the prompt, not just the allowlist.** A tools
   allowlist is necessary but not sufficient: Bash grants file writes via
   redirection (`> file`, `2> file`, `--out=`). A read-only agent's prompt
   must say so explicitly and direct any probe output/captures to the
   session scratchpad, never into repos or the vault. (Learned 2026-07-03:
   an auditor's stderr capture landed in the skills repo and got committed.)
5. **Second-brain knowledge layer (required).** Every agent leverages the
   OKF vault at `~/Library/CloudStorage/Dropbox/Documents/Obsidian/` in both
   directions: **consume** — before judging, consult the vault articles
   relevant to its domain (house decisions, platform gotchas) and cite them
   by vault path when they inform a finding; **feed** — when evidence
   contradicts a vault article, emit an INFO line naming it as a
   `curate-knowledge` candidate. Agents never write to the vault themselves;
   all vault writes stay behind curate-knowledge's human gate. Handle the
   CloudStorage-unmounted transient (vault path absent → note it in one
   line, proceed without).
6. **Delegate procedure to skills, by reference.** If a skill already
   encodes the how (audit rubric, groom rules), the agent reads and follows
   that skill's files in its report-only/`--agent` posture — it does not
   duplicate the procedure into its own prompt, so the skill stays the
   single source of truth.
7. **Output contract addressed to the coordinator.** The final message is
   consumed by the spawning model, not a human: raw structured data in a
   stated format, no preamble, no politeness. Honest empty results (PASS /
   clean) are valid outcomes — never manufacture findings to look thorough.
8. **Workers report; coordinators write.** Fan-out workers are read-only by
   default. Disposition of findings — edits, archives, deletions — belongs
   to the coordinator, behind the same human gates the skills enforce
   (curate-knowledge per-article confirmation, consent-gated repo writes).
9. **Findings are unverified until cross-checked.** A single agent's verdict
   is a claim, not a fact: the first suite sweep's one missed bug was caught
   only by coordinator re-verification. For decisions that matter, the
   coordinator verifies directly or fans out an adversarial second pass.
10. **Model field: inherit by default.** Omit `model:` so the agent runs on
    the session model; pin a smaller model only for genuinely mechanical
    work, and record why in the definition.

## H. Audit rubric

When auditing an agent definition (hand-check or a future mode of
audit-skill):

- Frontmatter: strict-YAML valid; `name` == filename stem; description
  states unit of work + return shape + never-does; `tools` is minimal.
- Prompt: read-only stated explicitly if the tool set implies it
  (including the redirection rule); knowledge layer present (consume +
  feed + unmounted transient); output contract format stated; honest-PASS
  line present; delegation by reference where a skill owns the procedure.
- Sediment: the definition duplicates no skill procedure and no other
  agent's scope.

## I. Severity guide

- **HIGH** — agent invisible to the harness (frontmatter unreadable), or a
  constraint gap that lets a worker mutate user-owned surfaces (missing
  read-only/redirection rule on a repo-touching agent).
- **MEDIUM** — description misroutes (wrong unit of work, stale claims);
  missing knowledge layer; output contract absent so the coordinator gets
  prose instead of data.
- **LOW** — strict-YAML latent (lenient parse still works); heavyweight
  description; missing honest-PASS line.
