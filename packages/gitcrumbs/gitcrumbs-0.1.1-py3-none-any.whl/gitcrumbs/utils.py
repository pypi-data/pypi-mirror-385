from __future__ import annotations
import os, json, sqlite3, subprocess, hashlib, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ShellError(RuntimeError): ...
class NotAGitRepo(RuntimeError): ...
class BareRepoUnsupported(RuntimeError): ...

# -----------------------------
# Shell helpers
# -----------------------------

def run_git(repo: Path, *args: str, check: bool = True, text: bool = True) -> str:
    cmd = ["git", "-C", str(repo), *args]
    p = subprocess.run(cmd, capture_output=True, text=text)
    if check and p.returncode != 0:
        raise ShellError(f"git {' '.join(args)} failed:\n{p.stderr}")
    return p.stdout

def try_git(repo: Path, *args: str) -> tuple[str, int, str]:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return p.stdout, p.returncode, p.stderr

# -----------------------------
# Repo discovery & safety
# -----------------------------

def ensure_repo_root(cwd: Optional[Path] = None) -> Path:
    cwd = Path.cwd() if cwd is None else Path(cwd)
    out, rc, _ = try_git(cwd, "rev-parse", "--show-toplevel")
    if rc != 0 or not out.strip():
        raise NotAGitRepo("Not inside a Git working tree.")
    root = Path(out.strip())

    bare, rc2, _ = try_git(root, "rev-parse", "--is-bare-repository")
    if rc2 == 0 and bare.strip() == "true":
        raise BareRepoUnsupported("Bare repositories are not supported (no working tree).")
    return root

def git_dir(repo: Path) -> Path:
    out = run_git(repo, "rev-parse", "--git-dir").strip()
    return (repo / out).resolve()

def state_dir(repo: Path) -> Path:
    d = git_dir(repo) / "gitcrumbs"
    d.mkdir(parents=True, exist_ok=True)
    return d

def db_path(repo: Path) -> Path:
    return state_dir(repo) / "gitcrumbs.db"

def tracker_state_path(repo: Path) -> Path:
    return state_dir(repo) / "tracker_state.json"

def restore_lock_path(repo: Path) -> Path:
    return state_dir(repo) / "restore.lock"

# -----------------------------
# SQLite
# -----------------------------

import sqlite3

def connect_db(repo: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(repo))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS snapshot (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      branch TEXT,
      head_commit TEXT,
      summary TEXT,
      restored_from_snapshot_id INTEGER NULL,
      FOREIGN KEY(restored_from_snapshot_id) REFERENCES snapshot(id)
    );

    CREATE TABLE IF NOT EXISTS file_state (
      snapshot_id INTEGER,
      path TEXT,
      status TEXT,            -- 'T' tracked, 'U' untracked, 'D' deleted
      blob_sha TEXT,          -- git object id for content at snapshot time (if applicable)
      size INTEGER NULL,
      mtime INTEGER NULL,
      PRIMARY KEY(snapshot_id, path),
      FOREIGN KEY(snapshot_id) REFERENCES snapshot(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS meta (
      key TEXT PRIMARY KEY,
      value TEXT
    );
    """)
    conn.commit()

# -----------------------------
# JSON state
# -----------------------------

def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)

def load_tracker_state(repo: Path) -> dict:
    p = tracker_state_path(repo)
    if not p.exists():
        return {
            "baseline_fingerprint": None,
            "baseline_snapshot_id": None,
            "suppress_until_change": False,
            "restored_from_snapshot_id": None,
            "last_seen_fingerprint": None,
            "last_seen_time": None,
        }
    try:
        return json.loads(p.read_text())
    except Exception:
        return {
            "baseline_fingerprint": None,
            "baseline_snapshot_id": None,
            "suppress_until_change": False,
            "restored_from_snapshot_id": None,
            "last_seen_fingerprint": None,
            "last_seen_time": None,
        }

# -----------------------------
# Git state helpers
# -----------------------------

def current_branch_and_head(repo: Path) -> tuple[str, str]:
    b_out, b_rc, _ = try_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    branch = b_out.strip() if b_rc == 0 and b_out.strip() else "DETACHED"
    h_out, h_rc, _ = try_git(repo, "rev-parse", "--verify", "HEAD")
    head = h_out.strip() if h_rc == 0 and h_out.strip() else "UNBORN"
    return branch, head

def index_locked(repo: Path) -> bool:
    return (git_dir(repo) / "index.lock").exists()

def in_merge_or_rebase(repo: Path) -> bool:
    g = git_dir(repo)
    return any((g / p).exists() for p in ["MERGE_HEAD", "rebase-merge", "rebase-apply"])

# -----------------------------
# Manifest & fingerprint
# -----------------------------

def compute_manifest(repo: Path) -> Tuple[Dict[str, Tuple[str,str,int,int]], List[str]]:
    manifest: Dict[str, Tuple[str,str,int,int]] = {}

    # Tracked from index
    ls = run_git(repo, "ls-files", "-s", "-z")
    items = [x for x in ls.split("\0") if x]
    for ent in items:
        try:
            head, path = ent.split("\t", 1)
            parts = head.split()
            blob = parts[1]
            p = (repo / path)
            try:
                st = p.stat()
                size, mtime = st.st_size, int(st.st_mtime)
            except FileNotFoundError:
                size, mtime = 0, 0
            manifest[path] = ('T', blob, size, mtime)
        except Exception:
            continue

    # Unstaged modifications
    diff_files = run_git(repo, "diff-files", "--name-only", "-z")
    for path in [x for x in diff_files.split("\0") if x]:
        p = (repo / path)
        if p.exists():
            blob = run_git(repo, "hash-object", "-w", "--", path).strip()
            st = p.stat()
            manifest[path] = ('T', blob, st.st_size, int(st.st_mtime))
        else:
            manifest[path] = ('D', "DELETED", 0, 0)

    # Tracked deletions
    deleted = run_git(repo, "ls-files", "-d", "-z")
    for path in [x for x in deleted.split("\0") if x]:
        manifest[path] = ('D', "DELETED", 0, 0)

    # Untracked (exclude ignored)
    untracked = run_git(repo, "ls-files", "-o", "--exclude-standard", "-z")
    for path in [x for x in untracked.split("\0") if x]:
        p = (repo / path)
        if p.is_file():
            try:
                blob = run_git(repo, "hash-object", "-w", "--", path).strip()
                st = p.stat()
                manifest[path] = ('U', blob, st.st_size, int(st.st_mtime))
            except ShellError:
                try:
                    st = p.stat()
                    manifest[path] = ('U', "UNHASHED", st.st_size, int(st.st_mtime))
                except FileNotFoundError:
                    pass
        elif p.is_symlink():
            try:
                target = os.readlink(p)
                blob = hashlib.sha256(("SYMLINK->"+target).encode()).hexdigest()
                st = p.lstat()
                manifest[path] = ('U', blob, st.st_size, int(st.st_mtime))
            except OSError:
                pass

    order = sorted(manifest.keys())
    return manifest, order

def compute_fingerprint(repo: Path) -> str:
    branch, head = current_branch_and_head(repo)
    manifest, order = compute_manifest(repo)

    # IMPORTANT: For tracked entries, fingerprint on content hash only (ignore mtime/size).
    # For untracked, include size/mtime because there is no index baseline.
    lines: List[str] = [f"branch={branch}", f"head={head}"]
    for path in order:
        status, blob, size, mtime = manifest[path]
        if status == 'T' or status == 'D':
            lines.append(f"{status}|{path}|{blob}")
        else:  # 'U'
            lines.append(f"{status}|{path}|{blob}|{size}|{mtime}")
    data = ("\n".join(lines)).encode()
    return hashlib.sha256(data).hexdigest()

# -----------------------------
# Snapshot ops
# -----------------------------

def create_snapshot(repo: Path, restored_from_snapshot_id: Optional[int] = None) -> int:
    conn = connect_db(repo)
    init_schema(conn)

    branch, head = current_branch_and_head(repo)
    manifest, order = compute_manifest(repo)

    mods = sum(1 for p in order if manifest[p][0] == 'T')
    adds = sum(1 for p in order if manifest[p][0] == 'U')
    dels = sum(1 for p in order if manifest[p][0] == 'D')
    summary = f"{adds} added, {mods} tracked/modified, {dels} deleted"

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO snapshot(branch, head_commit, summary, restored_from_snapshot_id) VALUES(?,?,?,?)",
        (branch, head, summary, restored_from_snapshot_id),
    )
    snap_id = int(cur.lastrowid)

    if order:
        rows = []
        for path in order:
            status, blob, size, mtime = manifest[path]
            rows.append((snap_id, path, status, blob, size, mtime))
        cur.executemany(
            "INSERT INTO file_state(snapshot_id, path, status, blob_sha, size, mtime) VALUES(?,?,?,?,?,?)",
            rows,
        )
    conn.commit()
    conn.close()
    return snap_id

def list_snapshots(repo: Path):
    conn = connect_db(repo)
    init_schema(conn)
    cur = conn.cursor()
    cur.execute("SELECT id, created_at, branch, summary, restored_from_snapshot_id FROM snapshot ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_snapshot_manifest(repo: Path, snap_id: int):
    conn = connect_db(repo)
    cur = conn.cursor()
    cur.execute(
        "SELECT path, status, blob_sha, size, mtime FROM file_state WHERE snapshot_id=?",
        (snap_id,),
    )
    out = {}
    for path, status, blob, size, mtime in cur.fetchall():
        out[path] = (status, blob, size if size is not None else 0, mtime if mtime is not None else 0)
    conn.close()
    return out

def branch_exists(repo: Path, name: str) -> bool:
    out, rc, _ = try_git(repo, "show-ref", "--verify", f"refs/heads/{name}")
    return rc == 0

def restore_snapshot(repo: Path, snap_id: int, purge: bool = True) -> None:
    """Restore files from snapshot with a lock to avoid tracker races."""
    # Create lock
    lock = restore_lock_path(repo)
    try:
        lock.write_text(str(time.time()))
    except Exception:
        pass

    try:
        # Load snapshot header
        conn = connect_db(repo)
        cur = conn.cursor()
        cur.execute("SELECT branch, head_commit FROM snapshot WHERE id=?", (snap_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            raise RuntimeError(f"Snapshot {snap_id} not found")
        branch, head = row

        # Switch branch/commit safely
        if head != "UNBORN":
            if branch != "DETACHED" and branch_exists(repo, branch):
                try_git(repo, "checkout", branch)
            else:
                try_git(repo, "checkout", "--detach", head)

        manifest = get_snapshot_manifest(repo, snap_id)
        wanted_paths = set(manifest.keys())

        # Write files
        for path, (status, blob, _, _) in manifest.items():
            p = repo / path
            p.parent.mkdir(parents=True, exist_ok=True)
            if status == 'D':
                try:
                    if p.exists():
                        p.unlink()
                except Exception:
                    pass
                continue
            if blob in ("UNHASHED", "DELETED"):
                continue
            out, rc, err = try_git(repo, "cat-file", "blob", blob)
            if rc != 0:
                try:
                    note = p.with_suffix(p.suffix + ".gitcrumbs.missing")
                    note.write_text(f"Missing blob {blob}\n{err}")
                except Exception:
                    pass
                continue
            tmp = p.with_suffix(p.suffix + ".gitcrumbs.tmp")
            tmp.write_text(out) if isinstance(out, str) else tmp.write_bytes(out)  # type: ignore
            tmp.replace(p)

        if purge:
            for root, dirs, files in os.walk(repo):
                if ".git" in dirs:
                    dirs.remove(".git")
                for f in files:
                    rel = str(Path(root, f).relative_to(repo))
                    if rel not in wanted_paths:
                        try:
                            (repo / rel).unlink()
                        except Exception:
                            pass
    finally:
        # Remove lock
        try:
            if lock.exists():
                lock.unlink()
        except Exception:
            pass
