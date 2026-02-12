Experimental Test Plan: Directory mtime Propagation and Change Detection Feasibility
====================================================================================

Purpose
-------
This document defines a structured experimental methodology to determine whether
directory modification timestamps (mtime) can be used as a reliable hierarchical
change-detection signal on a network-mounted production file server. The results
of these tests will directly determine which filesystem change detection algorithms
are safe and effective for deployment.

This is a filesystem semantics validation exercise, not an implementation task.

---------------------------------------------------------------------
1. System Under Test
---------------------------------------------------------------------

Directory Structure:

/ROOT
   /Production_A
       /Project_1
       /Project_2
   /Production_B
       /Project_X

Target files: .mov

Filesystem type: Network-mounted (SMB/NFS/other)

---------------------------------------------------------------------
2. Core Research Question
---------------------------------------------------------------------

Can directory mtimes be used as a reliable hierarchical signal for detecting
file changes inside project folders without scanning entire directory trees?

---------------------------------------------------------------------
3. Hypotheses
---------------------------------------------------------------------

H1: Project directory mtime updates when a file is created inside the project.

H2: Project directory mtime updates when a file is deleted inside the project.

H3: Project directory mtime updates when a file is renamed inside the project.

H4: Project directory mtime updates when an existing file is modified in-place.

H5: Production directory mtime updates when any project inside it changes.

H6: Metadata propagation delay is negligible (< polling interval).

H7: mtime updates are consistent (no intermittent failures).

---------------------------------------------------------------------
4. Experimental Actions
---------------------------------------------------------------------

For each test, record timestamps before and after the action.

Test A — File Creation
Action: Create a new .mov file in Project_1

Test B — File Deletion
Action: Delete a .mov file in Project_1

Test C — File Rename
Action: Rename a .mov file in Project_1

Test D — In-Place File Modification
Action: Modify an existing .mov file without renaming

Test E — Project Folder Creation
Action: Create a new Project folder

Test F — Cross-Project Move
Action: Move a .mov file from Project_1 to Project_2

Test G — No Activity Control
Action: No changes during interval

---------------------------------------------------------------------
5. Observations to Record
---------------------------------------------------------------------

For each test, record:

| Event | Project mtime changed? | Production mtime changed? | Delay observed |
|------|------------------------|---------------------------|----------------|

---------------------------------------------------------------------
6. Expected Outcome Matrix
---------------------------------------------------------------------

Case 1 — Ideal Propagation

All of H1–H5 true

Implication:
Full hierarchical mtime pruning is viable.

Algorithm allowed:
Production → Project → File-level scan only when flagged.

---------------------------------------------------------

Case 2 — Project-level Reliable, Production-level Not

H1–H4 true, H5 false

Implication:
Cannot prune at production level, but project-level pruning works.

Algorithm:
Scan project mtimes only.

---------------------------------------------------------

Case 3 — Only Structural Changes Trigger mtime

H1–H3 true, H4 false

Implication:
In-place file edits invisible to directory-level detection.

Algorithm:
Use project mtime + file-level snapshot diff.

---------------------------------------------------------

Case 4 — Weak Propagation

H1–H4 inconsistent or delayed

Implication:
Metadata caching or FS semantics unreliable.

Algorithm:
Merkle-style subtree hashing required.

---------------------------------------------------------

Case 5 — No Reliable Directory Signals

Most hypotheses false

Implication:
Directory metadata unusable.

Algorithm:
Full snapshot differencing or server-side agent required.

---------------------------------------------------------------------
7. Edge Cases and Failure Modes
---------------------------------------------------------------------

E1: Large file still being written — mtime may update multiple times.
Mitigation: Ignore files whose mtime < N seconds old.

E2: NAS metadata caching delays
Mitigation: Increase polling interval and re-test.

E3: Client clock skew vs server clock
Mitigation: Compare relative deltas, not absolute time.

E4: Permission changes
These may update directory mtime unexpectedly.

E5: Hidden system files (.DS_Store, temp files)
May create false positives.

E6: Atomic rename workflows
Often update directory mtime reliably — preferred workflow.

---------------------------------------------------------------------
8. Success Criteria
---------------------------------------------------------------------

We consider directory-based pruning viable if:

- Project directory mtime updates for all structural operations
- In-place edits either update mtime OR can be detected via file-level diff
- Metadata propagation delay < polling interval
- False negatives < acceptable threshold

---------------------------------------------------------------------
9. Final Decision Framework
---------------------------------------------------------------------

After experiments, choose:

If H1–H4 true → Use hierarchical mtime pruning

If H4 false but others true → Use mtime + snapshot diff

If inconsistent → Use Merkle hashing

If all false → Use full snapshot or server-side change feed

---------------------------------------------------------------------
10. Deliverable from Experiment
---------------------------------------------------------------------

Produce a summary table:

| Hypothesis | Result | Reliable? | Notes |
|-----------|--------|-----------|-------|

Followed by recommended algorithm tier.
