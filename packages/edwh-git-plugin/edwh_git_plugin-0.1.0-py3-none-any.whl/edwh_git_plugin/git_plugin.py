from edwh import confirm, task
from invoke import Context
from tabulate import tabulate
from termcolor import colored, cprint


@task()
def compare(ctx: Context):
    """
    Compare the current branch to all remote branches (behind | ahead).
    Shows colored results:
      - Red for behind > 0
      - Green for ahead > 0
      - Dim gray for equal (in sync)
    """

    # Update remote tracking info
    ctx.run("git fetch --all --prune", hide=True, warn=True)

    # Detect current branch
    current_branch = ctx.run("git rev-parse --abbrev-ref HEAD", hide=True).stdout.strip()

    # Get all remote branches
    remote_branches_output = (
        ctx.run("git for-each-ref --format='%(refname:short)' refs/remotes/", hide=True).stdout.strip().splitlines()
    )

    results = []

    for full_branch_name in remote_branches_output:
        if "/" not in full_branch_name:
            continue

        remote_name, branch_name = full_branch_name.split("/", 1)

        behind_count = (
            ctx.run(f"git rev-list --count HEAD..{full_branch_name}", hide=True, warn=True).stdout.strip() or "0"
        )

        ahead_count = (
            ctx.run(f"git rev-list --count {full_branch_name}..HEAD", hide=True, warn=True).stdout.strip() or "0"
        )

        behind_count = int(behind_count)
        ahead_count = int(ahead_count)

        # Apply color
        if behind_count > 0:
            behind_display = colored(str(behind_count), "red")
        else:
            behind_display = colored(str(behind_count), "white", attrs=["dark"])

        if ahead_count > 0:
            ahead_display = colored(str(ahead_count), "green")
        else:
            ahead_display = colored(str(ahead_count), "white", attrs=["dark"])

        results.append({"Remote": remote_name, "Branch": branch_name, "Behind": behind_display, "Ahead": ahead_display})

    # Sort results for readability
    results.sort(key=lambda row: (row["Remote"], row["Branch"]))

    # Display table
    print(tabulate(results, headers="keys", tablefmt="github"))

    print(f"\n📘 Comparing your current branch: {colored(current_branch, 'blue')}\n")
    print("ℹ️  'Behind' = commits your branch is missing from the remote (red)")
    print("ℹ️  'Ahead'  = commits your branch has that the remote doesn’t (green)")
    print("⚪  Zero values (gray) mean both are in sync\n")


@task()
def undo(ctx: Context, commit_hash: str):
    """
    Undo a commit safely.

    - If commit is pushed: creates a revert commit after confirmation.
    - If commit is local: resets commit (optionally keeping changes).
    """
    # Check if commit exists
    try:
        ctx.run(f"git cat-file -t {commit_hash}", hide=True)
    except Exception:
        cprint(f"❌ Commit {commit_hash} does not exist.", "red")
        exit(1)

    # Check if commit is pushed
    branches_containing_commit = (
        ctx.run(f"git branch -r --contains {commit_hash}", hide=True).stdout.strip().splitlines()
    )

    is_pushed = len(branches_containing_commit) > 0

    keep_changes_answer = confirm("Do you want to keep the changes in your working directory? [Y/n]", default=True)

    if is_pushed:
        cprint(
            f"⚠️  Commit {commit_hash} is already pushed to remote(s): {', '.join(branches_containing_commit)}", "yellow"
        )
        create_revert = confirm("Do you want to create a revert commit? [y/N]", default=False)

        if create_revert:
            ctx.run(f"git revert {commit_hash}")
            cprint(f"✅ Revert commit created for {commit_hash}", "green")
        else:
            cprint("❌ Aborted undo for pushed commit.", "red")
    else:
        # Local commit, safe to reset
        reset_mode = "--soft" if keep_changes_answer else "--mixed"
        ctx.run(f"git reset {reset_mode} {commit_hash}^")
        cprint(
            f"✅ Commit {commit_hash} undone. {'Changes kept' if keep_changes_answer else 'Changes moved to working directory'}",
            "green",
        )


@task(aliases=("unpushed",))
def drift(ctx: Context):
    """
    Show divergence of all local branches compared to their upstream remotes.
    Alias: unpushed
    Columns: Remote | Remote Branch | Local Branch | Behind | Ahead
    """

    # Get all local branches
    local_branches = (
        ctx.run("git for-each-ref --format='%(refname:short)' refs/heads/", hide=True).stdout.strip().splitlines()
    )

    # Get list of remotes
    remotes = ctx.run("git remote", hide=True).stdout.strip().splitlines()

    # Get all remote branches for existence check (without refs/heads/)
    remote_branches_raw = ctx.run("git ls-remote --heads", hide=True).stdout.strip().splitlines()
    remote_branches = [line.split()[1].replace("refs/heads/", "") for line in remote_branches_raw]

    results = []

    for local_branch in local_branches:
        # Get upstream safely
        upstream_result = ctx.run(
            f"git for-each-ref --format='%(upstream:short)' refs/heads/{local_branch}", hide=True, warn=True
        )
        upstream_full = upstream_result.stdout.strip().replace("@{u}", "")

        if not upstream_full:
            # No upstream
            remote_name = "-"
            remote_branch_name = "-"
            ahead_display = colored("-", "white", attrs=["dark"])
            behind_display = colored("-", "white", attrs=["dark"])
        else:
            # Split upstream into remote + branch
            if "/" in upstream_full:
                possible_remote, possible_branch = upstream_full.split("/", 1)
            else:
                possible_remote, possible_branch = "-", upstream_full

            # Check if upstream branch exists on remote
            upstream_exists = possible_branch in remote_branches and possible_remote in remotes

            if not upstream_exists:
                remote_name = "-"
                remote_branch_name = "-"
                ahead_display = colored("-", "white", attrs=["dark"])
                behind_display = colored("-", "white", attrs=["dark"])
            else:
                remote_name = possible_remote
                remote_branch_name = possible_branch

                # Count ahead/behind safely with quoting
                ahead_output = ctx.run(
                    f"git rev-list --count '{upstream_full}'..'{local_branch}'", hide=True, warn=True
                ).stdout.strip()
                behind_output = ctx.run(
                    f"git rev-list --count '{local_branch}'..'{upstream_full}'", hide=True, warn=True
                ).stdout.strip()

                ahead_count = int(ahead_output or 0)
                behind_count = int(behind_output or 0)

                # Color coding
                if ahead_count > 0 and behind_count == 0:
                    ahead_display = colored(str(ahead_count), "green")
                    behind_display = colored(str(behind_count), "white", attrs=["dark"])
                elif behind_count > 0 and ahead_count == 0:
                    ahead_display = colored(str(ahead_count), "white", attrs=["dark"])
                    behind_display = colored(str(behind_count), "red")
                elif ahead_count > 0 and behind_count > 0:
                    ahead_display = colored(str(ahead_count), "green")
                    behind_display = colored(str(behind_count), "red")
                else:
                    ahead_display = colored("0", "white", attrs=["dark"])
                    behind_display = colored("0", "white", attrs=["dark"])

        results.append(
            {
                "Remote": remote_name,
                "Remote Branch": remote_branch_name,
                "Local Branch": local_branch,
                "Behind": behind_display,
                "Ahead": ahead_display,
            }
        )

    # Sort by Remote, Remote Branch, Local Branch
    results.sort(key=lambda row: (row["Remote"], row["Remote Branch"], row["Local Branch"]))

    # Print table
    print(tabulate(results, headers="keys", tablefmt="github"))

    print("\nℹ️  'Ahead' = commits local branch has not pushed (green)")
    print("ℹ️  'Behind' = commits remote has not pulled (red)")
    print("⚪  Zero = branch fully synced\n")
