from __future__ import annotations
import time
import shutil
import os
from pathlib import Path
import typer
from rich import print as rprint
from rich.table import Table

from gitcrumbs.utils import (
    ensure_repo_root, connect_db, init_schema, create_snapshot, list_snapshots,
    compute_fingerprint, load_tracker_state, atomic_write_json, restore_snapshot,
    NotAGitRepo, BareRepoUnsupported, index_locked, in_merge_or_rebase,
    restore_lock_path, state_dir
)

app = typer.Typer(
    help=(
        "gitcrumbs — record durable working-tree snapshots for a Git repo, "
        "list/diff/restore them, and auto-track stable changes."
    )
)

def _anchor_after_restore(repo: Path, snap_id: int):
    """Anchor tracker baseline to the given snapshot after a restore."""
    fp = compute_fingerprint(repo)
    state = load_tracker_state(repo)
    state.update({
        "baseline_fingerprint": fp,
        "baseline_snapshot_id": snap_id,
        "suppress_until_change": True,
        "restored_from_snapshot_id": snap_id,
        "last_seen_fingerprint": fp,
        "last_seen_time": time.time(),
    })
    atomic_write_json(Path(repo / ".git/gitcrumbs/tracker_state.json"), state)

def _ordered_snapshot_ids(repo: Path):
    rows = list_snapshots(repo)
    return [sid for (sid, *_rest) in rows]

@app.command(help="Initialize .git/gitcrumbs/ (creates SQLite DB and config).")
def init():
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)
    conn = connect_db(repo); init_schema(conn); conn.close()
    rprint(f"Initialized gitcrumbs at {repo} (.git/gitcrumbs)")

@app.command(help="Create a snapshot of the current working state (manual).")
def snapshot():
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)
    snap_id = create_snapshot(repo)
    fp = compute_fingerprint(repo)
    state = load_tracker_state(repo)
    state.update({
        "baseline_fingerprint": fp,
        "baseline_snapshot_id": snap_id,
        "suppress_until_change": False,
        "restored_from_snapshot_id": None,
        "last_seen_fingerprint": fp,
        "last_seen_time": time.time(),
    })
    atomic_write_json(Path(repo / ".git/gitcrumbs/tracker_state.json"), state)
    rprint(f"Snapshot created: {snap_id}")

@app.command(help="Show all snapshots with summary info (chronological).")
def timeline():
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)
    rows = list_snapshots(repo)
    if not rows:
        rprint("[yellow]No snapshots yet.[/yellow]"); raise typer.Exit(0)
    t = Table("ID", "Created", "Branch", "Summary", "Resumed-From")
    for sid, created, branch, summary, restored_from in rows:
        t.add_row(str(sid), created, branch or "?", summary or "", str(restored_from) if restored_from else "")
    rprint(t)

@app.command(help="Show tracker status and the current snapshot cursor (baseline).")
def status():
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)
    rows = list_snapshots(repo); last = rows[-1] if rows else None
    state = load_tracker_state(repo)
    rprint(f"[bold]Repo:[/bold] {repo}")
    rprint(f"[bold]Last snapshot:[/bold] {last[0] if last else 'None'}")
    rprint(f"[bold]Tracker baseline set:[/bold] {bool(state.get('baseline_fingerprint'))}")
    rprint(f"[bold]Suppress-until-change:[/bold] {state.get('suppress_until_change')}")
    rprint(f"[bold]Cursor snapshot id:[/bold] {state.get('baseline_snapshot_id')}")

@app.command(help="Compare two snapshots (lists added/deleted/modified paths).")
def diff(a: int, b: int):
    from gitcrumbs.utils import get_snapshot_manifest
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)
    A = get_snapshot_manifest(repo, a); B = get_snapshot_manifest(repo, b)
    setA, setB = set(A.keys()), set(B.keys())
    added = sorted(list(setB - setA)); deleted = sorted(list(setA - setB))
    modified = []
    for p in sorted(setA & setB):
        if A[p][0] != B[p][0] or A[p][1] != B[p][1]:
            modified.append(p)
    t = Table("Category", "Count", "Files (first 5 shown)")
    t.add_row("Added", str(len(added)), ", ".join(added[:5]))
    t.add_row("Deleted", str(len(deleted)), ", ".join(deleted[:5]))
    t.add_row("Modified", str(len(modified)), ", ".join(modified[:5]))
    rprint(t)

@app.command(help="Restore to a specific snapshot (purges extra files by default).")
def restore(
    snap_id: int,
    purge: bool = typer.Option(True, "--purge/--no-purge", help="Delete files not in the snapshot (default: purge).", show_default=True),
):
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)
    if index_locked(repo):
        rprint("[yellow]Index appears locked (ongoing Git operation). Skipping restore.[/yellow]")
        raise typer.Exit(3)

    restore_snapshot(repo, snap_id, purge=purge)
    _anchor_after_restore(repo, snap_id)
    rprint(f"Restored snapshot {snap_id}. (purge={'on' if purge else 'off'}) Anchored; next durable change will create a new latest snapshot.")

# Navigation helpers (aliases grouped): "next" (alias: "n"), "previous" (alias: "p")

@app.command(help="Restore the next snapshot after the current cursor (alias: n).")
def next(
    purge: bool = typer.Option(True, "--purge/--no-purge", help="Delete files not in the target snapshot (default: purge).", show_default=True),
):
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)

    ids = _ordered_snapshot_ids(repo)
    if not ids:
        rprint("[yellow]No snapshots yet.[/yellow]"); raise typer.Exit(1)

    state = load_tracker_state(repo)
    cur = state.get("baseline_snapshot_id")

    target = None
    if cur is None:
        target = ids[0]
    else:
        try:
            idx = ids.index(cur)
            target = ids[idx + 1] if idx + 1 < len(ids) else None
        except ValueError:
            greater = [i for i in ids if i > cur]
            target = greater[0] if greater else None

    if target is None:
        rprint("[yellow]Already at the latest snapshot; no next snapshot available.[/yellow]")
        raise typer.Exit(0)

    if index_locked(repo):
        rprint("[yellow]Index appears locked (ongoing Git operation). Skipping restore.[/yellow]")
    else:
        restore_snapshot(repo, target, purge=purge)
        _anchor_after_restore(repo, target)
        rprint(f"Restored snapshot {target}. (purge={'on' if purge else 'off'})")

# hidden alias "n"
@app.command(name="n", hidden=True)
def _next_alias(
    purge: bool = typer.Option(True, "--purge/--no-purge", help="Delete files not in the target snapshot (default: purge).", show_default=True),
):
    return next(purge=purge)

@app.command(help="Restore the previous snapshot before the current cursor (alias: p).")
def previous(
    purge: bool = typer.Option(True, "--purge/--no-purge", help="Delete files not in the target snapshot (default: purge).", show_default=True),
):
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)

    ids = _ordered_snapshot_ids(repo)
    if not ids:
        rprint("[yellow]No snapshots yet.[/yellow]"); raise typer.Exit(1)

    state = load_tracker_state(repo)
    cur = state.get("baseline_snapshot_id")

    target = None
    if cur is None:
        target = ids[-1]
    else:
        try:
            idx = ids.index(cur)
            target = ids[idx - 1] if idx - 1 >= 0 else None
        except ValueError:
            smaller = [i for i in ids if i < cur]
            target = smaller[-1] if smaller else None

    if target is None:
        rprint("[yellow]Already at the earliest snapshot; no previous snapshot available.[/yellow]")
        raise typer.Exit(0)

    if index_locked(repo):
        rprint("[yellow]Index appears locked (ongoing Git operation). Skipping restore.[/yellow]")
    else:
        restore_snapshot(repo, target, purge=purge)
        _anchor_after_restore(repo, target)
        rprint(f"Restored snapshot {target}. (purge={'on' if purge else 'off'})")

# hidden alias "p"
@app.command(name="p", hidden=True)
def _previous_alias(
    purge: bool = typer.Option(True, "--purge/--no-purge", help="Delete files not in the target snapshot (default: purge).", show_default=True),
):
    return previous(purge=purge)

@app.command(help="Continuously track the repo; snapshot only when durable changes stabilize.")
def track(
    interval: int = typer.Option(30, help="Polling interval in seconds."),
    dwell: int = typer.Option(90, help="Required stability window in seconds before snapshot."),
):
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)

    state_path = Path(repo / ".git/gitcrumbs/tracker_state.json")
    rprint(f"Tracking repo at {repo} (interval={interval}s, dwell={dwell}s). Ctrl-C to stop.")
    try:
        while True:
            state = load_tracker_state(repo)

            if restore_lock_path(repo).exists() or index_locked(repo) or in_merge_or_rebase(repo):
                time.sleep(interval); continue

            fp = compute_fingerprint(repo); now = time.time()

            if fp != state.get("last_seen_fingerprint"):
                state["last_seen_fingerprint"] = fp
                state["last_seen_time"] = now

            stable = (state.get("last_seen_time") is not None) and (now - state["last_seen_time"] >= dwell)
            baseline = state.get("baseline_fingerprint")
            different_from_baseline = (baseline is None) or (fp != baseline)

            if stable:
                if state.get("suppress_until_change"):
                    if different_from_baseline:
                        snap_id = create_snapshot(repo, restored_from_snapshot_id=state.get("restored_from_snapshot_id"))
                        state.update({
                            "baseline_fingerprint": fp,
                            "baseline_snapshot_id": snap_id,
                            "suppress_until_change": False,
                            "restored_from_snapshot_id": None,
                        })
                        rprint(f"Snapshot created: {snap_id}")
                else:
                    if different_from_baseline:
                        snap_id = create_snapshot(repo, restored_from_snapshot_id=state.get("restored_from_snapshot_id"))
                        state.update({
                            "baseline_fingerprint": fp,
                            "baseline_snapshot_id": snap_id,
                            "restored_from_snapshot_id": None,
                        })
                        rprint(f"Snapshot created: {snap_id}")

            atomic_write_json(state_path, state)
            time.sleep(interval)
    except KeyboardInterrupt:
        rprint("Stopped tracking.")

@app.command(help="Remove .git/gitcrumbs from this repo (DB and metadata only; safe for Git history).")
def remove(
    yes: bool = typer.Option(False, "--yes", "-y", help="Do not prompt for confirmation."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed without deleting."),
):
    try:
        repo = ensure_repo_root()
    except (NotAGitRepo, BareRepoUnsupported) as e:
        rprint(f"[red]{e}[/red]"); raise typer.Exit(2)

    sdir = state_dir(repo)
    if not sdir.exists():
        rprint("Nothing to remove. (.git/gitcrumbs does not exist)")
        raise typer.Exit(0)

    # Summary
    total_files = 0
    total_bytes = 0
    for root, _dirs, files in os.walk(sdir):
        for f in files:
            total_files += 1
            try:
                total_bytes += (Path(root) / f).stat().st_size
            except OSError:
                pass

    size_mb = total_bytes / (1024*1024) if total_bytes else 0.0
    rprint(f"This will remove {total_files} files (~{size_mb:.2f} MB) under {sdir}")

    if dry_run:
        rprint("Dry-run: no changes made.")
        raise typer.Exit(0)

    if not yes:
        confirm = typer.confirm(f"Proceed to remove {sdir}?")
        if not confirm:
            rprint("Aborted."); raise typer.Exit(1)

    try:
        shutil.rmtree(sdir)
        rprint(f"Removed {sdir}")
    except Exception as e:
        rprint(f"[red]Failed to remove {sdir}: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
