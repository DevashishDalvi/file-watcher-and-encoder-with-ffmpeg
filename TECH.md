Efficient Incremental Change Detection in Large Network File Systems
====================================================================

Abstract
--------
This document presents a comprehensive technical analysis of the problem of detecting
new or modified .mov files in a large network-mounted filesystem where filesystem
event monitoring (e.g., watchdog, FSEvents, inotify) is unreliable or unavailable.
The report formalizes the problem, evaluates algorithmic solution families used in
industry systems, compares their computational and I/O characteristics, and proposes
a scalable hybrid architecture optimized for high-latency storage environments.

---------------------------------------------------------------------
1. Problem Definition
---------------------------------------------------------------------

1.1 Operational Context

Environment:
- Network-mounted file server (SMB/NFS or similar)
- Thousands of project directories
- Only .mov files are relevant
- Watchdog/event-based systems unreliable across mount boundary
- Recursive full-tree scans are too expensive

1.2 Core Objective

Given:
    T(n)   = current filesystem state
    S(n-1) = previously recorded state

Compute:
    Δ = T(n) − S(n-1)

Where Δ represents new, modified, or deleted .mov files.

Constraints:
- Minimize filesystem I/O
- Avoid full recursive scans when possible
- Scale efficiently as directory count grows
- Avoid excessive hashing of large media files

This is a hierarchical incremental state reconciliation problem
under limited observability.

---------------------------------------------------------------------
2. System Constraints and Failure Modes
---------------------------------------------------------------------

2.1 Constraints

- No trustworthy event stream
- Network latency amplifies directory traversal cost
- Directory mtime behavior may vary across filesystems
- Large files (.mov) are expensive to hash
- Change locality: small subset of projects change per cycle

2.2 Failure Modes to Avoid

- O(N) full-tree scanning per cycle
- Missing in-place file modifications
- Saturating network storage metadata operations
- CPU overload from unnecessary content hashing

---------------------------------------------------------------------
3. Algorithmic Foundations
---------------------------------------------------------------------

This problem intersects with:
- Incremental computation
- Backup system indexing
- Version control systems
- Distributed state reconciliation
- Hierarchical hashing structures

The goal is to make detection cost proportional to number of changes
rather than total namespace size.

---------------------------------------------------------------------
4. Algorithm Families
---------------------------------------------------------------------

4.1 Directory Metadata Heuristic (Shallow Change Filter)

Concept:
Use directory modification timestamps as a change indicator.

Algorithm:
For each directory D:
    if mtime(D) unchanged:
        skip subtree
    else:
        mark D dirty

Time Complexity:
O(number_of_directories)

Pros:
- Extremely low I/O
- Fast metadata-only operations
- Effective when changes are sparse

Cons:
- May miss in-place file edits if directory mtime not updated
- Heuristic, not authoritative

Used by:
- rsync (quick check stage)
- Build systems (Make, Ninja)

---------------------------------------------------------------------

4.2 Hierarchical Hashing (Merkle Trees)

Concept:
Represent filesystem as a Merkle tree:

file_hash = H(size, mtime, optional content)
dir_hash  = H(sorted(child_name + child_hash))

If dir_hash unchanged → entire subtree unchanged.

Time Complexity:
Best case: O(number_of_directories)
Worst case: O(total_files)

Advantages:
- Exact subtree change detection
- Early pruning of unchanged trees
- Industry-proven scalability

Disadvantages:
- Requires persistent hash storage
- Some hashing overhead

Used by:
- Git
- Borg Backup
- restic
- IPFS

---------------------------------------------------------------------

4.3 Snapshot Differencing

Concept:
Store snapshot S(n) of file metadata.
Compute S(n+1).
Perform sorted diff.

Algorithm:
- Collect metadata entries
- Sort entries
- Linear merge comparison

Complexity:
O(N log N) for sorting + O(N) diff

Pros:
- Exact detection
- Straightforward logic

Cons:
- Requires full traversal unless pre-filtered

Used by:
- Cloud synchronization engines (Dropbox, OneDrive)

---------------------------------------------------------------------

4.4 Filesystem Journaling

Concept:
Read change journal maintained by filesystem.

Complexity:
O(number_of_changes)

Pros:
- Ideal performance
- Event-driven

Cons:
- Not available across most network mounts

Examples:
- Windows USN Journal
- ZFS intent log

---------------------------------------------------------------------

4.5 Probabilistic Directory Summaries

Concept:
Represent directory state via Bloom filters or hash sketches.

Pros:
- Very fast comparisons
- Low memory footprint

Cons:
- False positives possible
- Complex implementation

Common in distributed storage research systems.

---------------------------------------------------------------------
5. Comparative Evaluation
---------------------------------------------------------------------

Method                     Accuracy    I/O Cost    Scalability
--------------------------------------------------------------
Dir mtime filter           Medium      Very Low    High
Merkle tree hashing        High        Medium      Very High
Snapshot differencing      High        High        Moderate
Filesystem journaling      Exact       Very Low    Excellent
Probabilistic summaries    Probabilistic Low       High

---------------------------------------------------------------------
6. Recommended Hybrid Architecture
---------------------------------------------------------------------

To optimize performance under network latency and sparse change
conditions, a layered strategy is recommended.

Layer 1 — Directory-Level Filter
---------------------------------
Use directory mtime heuristic to reduce candidate directories.

Result:
From N directories → K dirty directories (K << N).

Layer 2 — Metadata-Based Merkle Hashing
----------------------------------------
Compute subtree hashes only for dirty directories.
Prune unchanged subtrees immediately.

Layer 3 — Targeted Snapshot Differencing
-----------------------------------------
Within changed subtrees, diff only .mov files.
Track additions, modifications, deletions.

Pipeline Flow:

All Directories
      ↓
Directory mtime filter
      ↓
Dirty Directories
      ↓
Merkle subtree comparison
      ↓
Changed Subtrees
      ↓
.mov snapshot diff
      ↓
Final Change Set

This ensures runtime is proportional to number of changed directories,
not total tree size.

---------------------------------------------------------------------
7. Complexity Modeling
---------------------------------------------------------------------

Let:
D = number of project directories
F = total number of files
K = number of changed directories
C = number of changed files

Naive full scan:
O(F)

Hybrid approach:
O(D) directory stats +
O(size_of_subtrees_in_K) +
O(C log C)

When K << D and C << F,
overall cost approaches O(D + C).

---------------------------------------------------------------------
8. Engineering Recommendations
---------------------------------------------------------------------

Phase 1 — Implementation
- Directory mtime filter
- Metadata-only Merkle hashing
- Snapshot diff restricted to .mov files

Phase 2 — Optimization
- Persistent hash cache (SQLite or embedded DB)
- Adaptive polling interval
- Rate-limited parallel scanning

Phase 3 — Long-Term Improvements
- Investigate server-side change feed
- Encourage atomic file-write patterns (temp + rename)
- Consider lightweight server agent if possible

---------------------------------------------------------------------
9. Strategic Conclusion
---------------------------------------------------------------------

The problem is fundamentally not about file monitoring, but about
efficient hierarchical state reconciliation under constrained observation.

Event-driven solutions are ideal but unavailable.
Full scans are reliable but inefficient.

The optimal scalable solution is a hybrid algorithm combining:

1) Directory-level metadata filtering
2) Merkle-style hierarchical hashing
3) Targeted snapshot differencing

This architecture mirrors the design principles used in modern
backup systems, version control systems, and distributed storage platforms.

It ensures that system cost scales with change volume rather than
total namespace size, which is the critical requirement for
large network-mounted media repositories.
