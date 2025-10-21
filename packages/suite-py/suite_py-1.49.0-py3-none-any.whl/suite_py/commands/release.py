# -*- coding: utf-8 -*-
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from suite_py.commands import common
from suite_py.lib import logger, metrics
from suite_py.lib.handler import git_handler as git
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.changelog_handler import ChangelogHandler
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.version_handler import DEFAULT_VERSION, VersionHandler
from suite_py.lib.handler.youtrack_handler import YoutrackHandler


class Release:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-positional-arguments
    def __init__(
        self,
        action,
        project,
        captainhook,
        config,
        tokens,
        commit=None,
        interactive=False,
    ):
        self._action = action
        self._project = project
        self._config = config
        self._tokens = tokens
        # Optional commit (sha or short sha) to release instead of HEAD
        self._commit = commit
        # Whether to prompt the user to choose commit among unreleased ones
        self._interactive = interactive
        self._changelog_handler = ChangelogHandler()
        self._youtrack = YoutrackHandler(config, tokens)
        self._captainhook = captainhook
        self._github = GithubHandler(tokens)
        self._repo = self._github.get_repo(project)
        self._git = GitHandler(project, config)
        self._version = VersionHandler(self._repo, self._git, self._github)

    @metrics.command("release")
    def run(self):
        self._stop_if_prod_locked()
        self._git.fetch()

        if self._action == "create":
            self._create()

    def _stop_if_prod_locked(self):
        request = self._captainhook.status(self._project, "production")
        if request.status_code != 200:
            logger.error("Unable to determine lock status on master.")
            sys.exit(-1)

        request_object = request.json()
        if request_object["locked"]:
            logger.error(
                f"The project is locked in production by {request_object['by']}. Unable to continue."
            )
            sys.exit(-1)

    def _create(self):
        latest = self._version.get_latest_version()
        commits, new_version, message = self._gather_commits_and_version(latest)
        message = self._augment_message_with_changelog(new_version, message)
        message = common.ask_for_release_description(message)
        sha = self._resolve_target_sha(commits)
        self._create_release(new_version, message, sha)

    def _gather_commits_and_version(self, latest):
        """Return (commits, new_version, base_message)."""
        if latest == "":
            return self._first_release_flow()

        logger.info(f"The current release is {latest}")
        commits = self._github.get_commits_since_release(self._repo, latest)
        if not commits:
            logger.warning(
                "No commits found after the latest release tag; nothing to release."
            )
            sys.exit(0)
        # If user did not pass a target commit, ask interactively which commit to release.
        # Only perform interactive selection if user explicitly requested it
        if self._interactive:
            self._select_commit_if_needed(commits)
        commits = self._maybe_trim_commits(commits)
        _check_migrations_deploy(commits)
        message = self._build_commits_message(commits)
        logger.info(f"\nCommits list:\n{message}\n")
        if not prompt_utils.ask_confirm("Do you want to continue?"):
            sys.exit()
        new_version = self._version.select_new_version(latest, allow_prerelease=True)
        return commits, new_version, message

    def _first_release_flow(self):
        logger.warning(f"No tags found, I'm about to push the tag {DEFAULT_VERSION}")
        if not prompt_utils.ask_confirm(
            "Are you sure you want to continue?", default=False
        ):
            sys.exit()
        return [], DEFAULT_VERSION, f"First release with tag {DEFAULT_VERSION}"

    def _maybe_trim_commits(self, commits):
        if not self._commit:
            return commits
        try:
            resolved_commit = self._repo.get_commit(self._commit)
            target_sha = resolved_commit.sha
        except Exception:
            logger.error(
                f"The provided commit '{self._commit}' was not found in the repository."
            )
            sys.exit(-1)
        target_index = None
        for idx, c in enumerate(commits):
            if (
                c.sha == target_sha
                or getattr(c, "commit", None)
                and c.commit.sha == target_sha
            ):
                target_index = idx
                break
        if target_index is None:
            logger.error(
                "The specified commit is not part of the unreleased commits (i.e., not after the latest release)."
            )
            sys.exit(-1)
        # We want ONLY the selected commit and the older commits (towards the previous release),
        # excluding any *newer* commits that appear before it in the list.
        return commits[target_index:]

    def _select_commit_if_needed(self, commits):
        """Interactively ask the user which commit to release if none was provided.

        Presents the unreleased commits (newest first) allowing the user to pick a
        target commit. The chosen commit's SHA (full) is stored in `self._commit` so
        that downstream logic (_maybe_trim_commits / _resolve_target_sha) works
        unchanged.
        """
        if self._commit or not commits:
            return

        choices = []

        def build_choice(c, icon):
            summary = c.commit.message.splitlines()[0]
            return {
                "name": f"{icon} {c.sha[:8]} | {summary}",
                "value": c.sha,
            }

        with ThreadPoolExecutor(max_workers=min(8, len(commits))) as executor:
            future_map = {
                executor.submit(self._get_commit_status_icon, c.sha): c for c in commits
            }

            icon_results = {}
            for future in as_completed(future_map):
                c = future_map[future]
                try:
                    icon_results[c.sha] = future.result()
                except Exception:
                    icon_results[c.sha] = "?"
            for c in commits:
                choices.append(build_choice(c, icon_results.get(c.sha, "?")))

        subtitle = "(only one available)" if len(choices) == 1 else "(newest first):"
        selected = prompt_utils.ask_choices(
            f"Select commit to release {subtitle}", choices
        )
        self._commit = selected

    def _get_commit_status_icon(self, sha):
        """Return an icon representing the simplified CI status for a commit.

        Final exposed statuses (icons):
          success (✅), failure (❌), in_progress (🏗️), cancelled (🚫), unknown (❓)

        Everything else is folded into one of those buckets:
          pending / queued / waiting -> in_progress
          skipped / neutral -> unknown (unless at least one success present)
        Preference order for determining state:
          1. Check runs API
          2. Combined status API
          3. Fallback unknown
        """
        check_runs = self._safe_get_check_runs(sha)
        state = self._classify_from_check_runs(check_runs) if check_runs else None
        if state is None:
            state = self._classify_from_combined_status(sha)
        return self._icon_for_state(state)

    def _safe_get_check_runs(self, sha):
        try:
            commit = self._repo.get_commit(sha)
            return list(commit.get_check_runs())
        except Exception:
            return []

    def _classify_from_check_runs(self, check_runs):
        statuses = {r.status for r in check_runs if getattr(r, "status", None)}
        conclusions = {
            r.conclusion for r in check_runs if getattr(r, "conclusion", None)
        }

        if self._any_in_progress(statuses):
            return "in_progress"
        if self._any_failure(conclusions):
            return "failure"
        if "cancelled" in conclusions:
            return "cancelled"
        if self._is_success(conclusions):
            return "success"
        return "unknown"

    @staticmethod
    def _any_in_progress(statuses):
        return any(
            s in {"in_progress", "queued", "waiting", "pending"} for s in statuses
        )

    @staticmethod
    def _any_failure(conclusions):
        return any(
            c in {"failure", "timed_out", "action_required", "stale"}
            for c in conclusions
        )

    @staticmethod
    def _is_success(conclusions):
        return bool(conclusions) and (
            all(c == "success" for c in conclusions)
            or ("success" in conclusions and not Release._any_failure(conclusions))
        )

    def _classify_from_combined_status(self, sha):
        try:
            status = self._github.get_build_status(self._project, sha)
            combined = (status.state or "unknown").lower()
        except Exception:
            combined = "unknown"
        if combined in {"pending", "queued", "waiting", "in_progress"}:
            return "in_progress"
        if combined == "success":
            return "success"
        if combined == "failure":
            return "failure"
        if combined == "cancelled":
            return "cancelled"
        return "unknown"

    @staticmethod
    def _icon_for_state(state):
        icon_mapping = {
            "success": "✅",
            "failure": "❌",
            "in_progress": "🏗️",
            "cancelled": "🚫",
            "unknown": "❓",
        }
        return icon_mapping.get(state, "❓")

    @staticmethod
    def _build_commits_message(commits):
        return "\n".join(
            [
                "* " + c.commit.message.splitlines()[0] + " by " + c.commit.author.name
                for c in commits
            ]
        )

    def _augment_message_with_changelog(self, new_version, message):
        if not self._changelog_handler.changelog_exists():
            return message
        latest_tag, latest_entry = self._changelog_handler.get_latest_entry_with_tag()
        if latest_tag != new_version:
            if not prompt_utils.ask_confirm(
                "You didn't update your changelog, are you sure you want to proceed?"
            ):
                sys.exit()
            return message
        return f"{latest_entry}\n\n# Commits\n\n{message}"

    def _resolve_target_sha(self, commits):
        if not self._commit:
            return commits[0].commit.sha if commits else ""
        try:
            sha = self._repo.get_commit(self._commit).sha
        except Exception:
            logger.error(
                f"Unable to resolve commit '{self._commit}' during release creation."
            )
            sys.exit(-1)
        self._validate_target_commit_not_tagged(sha)
        return sha

    def _validate_target_commit_not_tagged(self, sha):
        try:
            for t in self._repo.get_tags():
                if t.commit.sha == sha:
                    logger.error(
                        f"The commit {sha[:7]} is already tagged with {t.name}. Aborting."
                    )
                    sys.exit(-1)
        except Exception:
            logger.warning("Could not verify if commit already tagged; continuing.")

    def _create_release(self, new_version, message, commit):
        new_release = self._repo.create_git_release(
            new_version,
            new_version,
            self._youtrack.replace_card_names_with_md_links(message),
            target_commitish=commit,
        )
        if new_release:
            logger.info(f"The release has been created! Link: {new_release.html_url}")

    def _manage_youtrack_card(self, version, countries):
        release_state = self._config.youtrack["release_state"]

        release_body = self._repo.get_release(version).body

        issue_ids = self._youtrack.get_ids_from_release_body(release_body)

        if len(issue_ids) > 0:
            update_youtrack_state = prompt_utils.ask_confirm(
                f"Do you want to move the associated cards to {release_state} state?",
                default=False,
            )

            for issue_id in issue_ids:
                try:
                    self._youtrack.comment(
                        issue_id,
                        f"Deploy in production of {self._project} in countries {countries} done with the release {version}",
                    )
                    if update_youtrack_state:
                        self._youtrack.update_state(issue_id, release_state)
                        logger.info(f"{issue_id} moved to {release_state}")
                except Exception:
                    logger.warning(
                        f"An error occurred while moving the card {issue_id} to {release_state}"
                    )
                repos_status = self._get_repos_status_from_issue(issue_id)
                if all(r["deployed"] for r in repos_status.values()):
                    try:
                        self._youtrack.update_deployed_field(issue_id)
                        logger.info("Custom field Deployed updated on YouTrack")
                    except Exception:
                        logger.warning(
                            "An error occurred while updating the custom field Deployed"
                        )

    def _get_repos_status_from_issue(self, issue_id):
        regex_pr = r"^PR .* -> https:\/\/github\.com\/primait\/(.*)\/pull\/([0-9]*)$"
        regex_deploy = r"^Deploy in production of (.*) in countries"
        comments = self._youtrack.get_comments(issue_id)
        repos_status = {}

        for c in comments:
            m = re.match(regex_pr, c["text"])
            if m:
                project = m.group(1)
                pr_number = int(m.group(2))
                repos_status[project] = {}
                repos_status[project]["pr"] = pr_number
                repos_status[project]["deployed"] = False
            m = re.match(regex_deploy, c["text"])
            if m:
                project = m.group(1)
                try:
                    repos_status[project]["deployed"] = True
                except Exception:
                    pass
        return repos_status

    def _tags_drifted(self, versions):
        for country, version in versions.items():
            for c, v in versions.items():
                if country == c:
                    continue
                if version is None or v is None or version.compare(v) != 0:
                    return True
        return False


def _check_migrations_deploy(commits):
    if not commits:
        logger.error("ERROR: no commit found")
        sys.exit(-1)
    elif len(commits) == 1:
        files_changed = git.files_changed_between_commits("--raw", f"{commits[0].sha}~")
    else:
        files_changed = git.files_changed_between_commits(
            f"{commits[-1].sha}~", commits[0].sha
        )
    if git.migrations_found(files_changed):
        logger.warning("WARNING: migrations detected in the code")
        if not prompt_utils.ask_confirm(
            "Are you sure you want to continue?", default=False
        ):
            sys.exit()
