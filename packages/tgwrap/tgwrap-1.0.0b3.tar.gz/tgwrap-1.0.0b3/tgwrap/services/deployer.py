"""Deployment and sync helpers."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime

import inquirer

from ..core.constants import DateTimeEncoder
from ..deploy import prepare_deploy_config, run_sync


class DeploymentService:
    """Encapsulate deployment-oriented workflows."""

    def __init__(
        self,
        *,
        printer,
        tg_file: str,
        latest_version: str,
        version_file: str,
        yaml_loader,
    ) -> None:
        self.printer = printer
        self.tg_file = tg_file
        self.latest_version = latest_version
        self.version_file = version_file
        self.yaml_loader = yaml_loader

    # Sync helpers -------------------------------------------------------

    def sync(
        self,
        *,
        source_stage: str,
        target_stage: str,
        source_domain: str | None,
        target_domain: str | None,
        module: str,
        auto_approve: bool,
        clean: bool,
        include_dotenv_file: bool,
        working_dir: str | None,
    ) -> None:
        """Synchronise a module between environments."""
        if target_domain and not source_domain:
            raise ValueError(
                "Providing a target domain while omitting the source domain is not supported!"
            )
        if source_domain and not target_domain:
            raise ValueError(
                "Providing a source domain while omitting the target domain is not supported!"
            )

        if target_domain and not target_stage:
            self.printer.verbose(
                "No target stage given, assume the same as source stage"
            )
            target_stage = source_stage

        if not source_domain and not target_domain and not target_stage:
            raise ValueError(
                "When not providing domains, you need to provide a target stage!"
            )

        working_dir = working_dir if working_dir else os.getcwd()
        source_path = os.path.join(working_dir, source_domain, source_stage, module, "")
        target_path = os.path.join(working_dir, target_domain, target_stage, module, "")

        run_sync(
            source_path=source_path,
            target_path=target_path,
            source_domain=source_domain,
            source_stage=source_stage,
            target_stage=target_stage,
            include_dotenv_file=include_dotenv_file,
            auto_approve=auto_approve,
            clean=clean,
            terragrunt_file=self.tg_file,
            verbose=self.printer.print_verbose,
        )

    def sync_dir(
        self,
        *,
        source_directory: str,
        target_directory: str,
        auto_approve: bool,
        clean: bool,
        include_dotenv_file: bool,
        working_dir: str | None,
    ) -> None:
        """Synchronise entire Terragrunt directories."""
        working_dir = working_dir if working_dir else os.getcwd()
        source_path = os.path.join(working_dir, source_directory, "")
        target_path = os.path.join(working_dir, target_directory, "")

        run_sync(
            source_path=source_path,
            target_path=target_path,
            auto_approve=auto_approve,
            clean=clean,
            include_dotenv_file=include_dotenv_file,
            terragrunt_file=self.tg_file,
            verbose=self.printer.print_verbose,
        )

    # Deploy -------------------------------------------------------------

    def deploy(
        self,
        *,
        manifest_file: str,
        version_tag: str | None,
        target_stages,
        include_global_config_files: bool,
        auto_approve: bool,
        working_dir: str | None,
    ) -> None:
        """Deploy Terragrunt sources for the requested stages."""
        try:
            temp_dir = os.path.join(tempfile.mkdtemp(prefix="tgwrap-"), "tg-source")

            working_dir = working_dir if working_dir else os.getcwd()
            manifest = self.yaml_loader(os.path.join(working_dir, manifest_file))

            source_dir = os.path.join(temp_dir, manifest["base_path"])

            try:
                source_config_dir = os.path.join(temp_dir, manifest["config_path"])
            except KeyError:
                source_config_dir = None

            version_tag, _, _ = self._clone_repo(
                repo=manifest["git_repository"],
                target_dir=temp_dir,
                version_tag=version_tag,
            )

            substacks = ["substacks", "sub_stacks"]
            for _, substack in manifest.get("sub_stacks", {}).items():
                substacks.append(substack["source"].split(os.path.sep)[0])
            substacks = set(substacks)

            substack_configs = manifest.get("sub_stacks", {})
            substack_configs.update(manifest.get("substacks", {}))

            for target_stage in target_stages:
                stage_target_dir = os.path.join(working_dir, "", target_stage)
                self.printer.header(f"Deploy stage {target_stage} to {stage_target_dir}...")
                try:
                    os.makedirs(stage_target_dir)
                except FileExistsError:
                    pass

                deploy_actions = {}
                deploy_global_configs = include_global_config_files
                target_stage_found = False

                for key, value in manifest["deploy"].items():
                    if target_stage not in value["applies_to_stages"]:
                        self.printer.verbose(
                            f"Target stage {target_stage} not applicable for action {key}."
                        )
                        continue

                    deploy_actions.update(
                        prepare_deploy_config(
                            step=key,
                            config=value,
                            source_dir=source_dir,
                            source_config_dir=source_config_dir,
                            target_dir=stage_target_dir,
                            target_stage=target_stage,
                            substacks=substacks,
                            substack_configs=substack_configs.items(),
                            tg_file_name=self.tg_file,
                            verbose=self.printer.print_verbose,
                        )
                    )
                    deploy_global_configs = value.get(
                        "include_global_config_files", deploy_global_configs
                    )
                    target_stage_found = True

                if target_stage_found and deploy_global_configs:
                    for gc, global_config in manifest.get(
                        "global_config_files", {}
                    ).items():
                        self.printer.verbose(f"Found global config : {gc}")

                        source_path = os.path.join(source_dir, global_config["source"])

                        target = global_config.get("target", global_config["source"])
                        target_path = os.path.dirname(
                            os.path.join(
                                working_dir,
                                target,
                            )
                        )
                        if os.path.exists(source_path):
                            deploy_actions[f"global configs -> {target}"] = {
                                "source": source_path,
                                "target": target_path,
                            }
                        else:
                            self.printer.warning(
                                f"Source path of global configs does not exist: {source_path}"
                            )
                else:
                    self.printer.verbose("Skipping global configs")

                if deploy_actions:
                    self.printer.header("Modules to deploy:")
                    self.printer.normal(
                        f'-> git repository: {manifest["git_repository"]}'
                    )
                    self.printer.normal(f"-> version tag: {version_tag}")
                    self.printer.normal("Modules:")
                    for key, value in deploy_actions.items():
                        self.printer.normal(f"--> {key}")

                    response = "n"
                    if not auto_approve:
                        response = input("\nDo you want to continue? (y/N) ")

                    if auto_approve or response.lower() == "y":
                        for value in deploy_actions.values():
                            run_sync(
                                source_path=value["source"],
                                target_path=value["target"],
                                excludes=value.get("excludes", []),
                                include_dotenv_file=True,
                                auto_approve=True,
                                clean=False,
                                terragrunt_file=self.tg_file,
                                verbose=self.printer.print_verbose,
                            )

        except KeyError as exc:
            self.printer.error(
                "Error interpreting the manifest file. Please ensure it uses the proper format. "
                f"Could not find element: {exc}"
            )
            if self.printer.print_verbose:
                raise
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-except
            self.printer.error(f"Unexpected error: {exc}")
            if self.printer.print_verbose:
                raise
            sys.exit(1)
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:  # pylint: disable=broad-except
                pass

    # Version checks ----------------------------------------------------

    def check_deployments(
        self,
        *,
        repo_url: str,
        levels_deep: int,
        working_dir: str | None,
        out: bool,
    ) -> None:
        """Report deployed versions relative to the source repository."""
        def locate_version_files(
            current_directory,
            found_files=None,
            root_directory=None,
            level=1,
            git_status="",
        ):
            found_files = found_files if found_files else []

            if os.path.basename(current_directory).startswith("."):
                return found_files

            if not root_directory:
                root_directory = current_directory

            if not git_status:
                self.printer.verbose(
                    f"Check for git status in directory {current_directory}"
                )
                cmd = "git status"
                rc = subprocess.run(
                    shlex.split(cmd),
                    cwd=current_directory,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                output = ("stdout: " + rc.stdout + "stderr: " + rc.stderr).lower()
                if "not a git repository" in output:
                    pass
                elif "branch is up to date" in output:
                    git_status = "up to date; "
                elif "head detached" in output:
                    git_status = "head detached; "
                elif "untracked files" in output:
                    git_status = git_status + "untracked files; "
                elif "changes to be committed" in output:
                    git_status = git_status + "staged changes; "
                elif "changes not staged for commit" in output:
                    git_status = git_status + "unstaged changes; "
                elif "branch is ahead of" in output:
                    git_status = git_status + "ahead of remote; "
                elif "branch is behind of" in output:
                    git_status = git_status + "behind remote; "
                elif "unmerged paths" in output:
                    git_status = git_status + "merge conflicts; "

            for entry in os.listdir(current_directory):
                full_entry = os.path.join(current_directory, entry)

                if os.path.isdir(full_entry) and level <= levels_deep:
                    found_files = locate_version_files(
                        current_directory=full_entry,
                        found_files=found_files,
                        root_directory=root_directory,
                        level=level + 1,
                        git_status=git_status,
                    )
                elif entry == self.version_file:
                    found_files.append(
                        {
                            "path": os.path.relpath(current_directory, root_directory),
                            "git_status": git_status,
                        }
                    )

            return found_files

        def get_all_versions(repo_dir, min_version=None):
            cmd = "git tag --sort='-refname:short' --format='%(refname:short) %(creatordate:iso8601)'"
            output = subprocess.check_output(
                shlex.split(cmd),
                text=True,
                cwd=repo_dir,
                universal_newlines=True,
            )

            timestamp_format = "%Y-%m-%d %H:%M:%S %z"
            tags = {}
            for line in output.splitlines():
                tag_name, created_date = line.split(" ", maxsplit=1)
                tags[tag_name] = {
                    "created_date": datetime.strptime(created_date, timestamp_format)
                }

                if tag_name == min_version:
                    break

            self.printer.verbose(f"Found {len(tags)} tags: {tags}")
            return tags

        try:
            working_dir = working_dir if working_dir else os.getcwd()
            self.printer.header(
                f"Check released versions (max {levels_deep} levels deep) in directory: {working_dir}"
            )

            found_files = locate_version_files(working_dir)

            versions = []
            for result in found_files:
                with open(
                    os.path.join(working_dir, result["path"], self.version_file),
                    encoding="utf-8",
                ) as file:
                    content = file.read()
                    tag_match = re.search(r'version_tag\s*=\s*"([^"]+)"', content)
                    if tag_match:
                        version_tag = tag_match.group(1)
                    else:
                        version_tag = "unknown"

                versions.append(
                    {
                        "path": result["path"],
                        "tag": version_tag,
                        "git_status": result.get("git_status"),
                    }
                )

            temp_dir = tempfile.mkdtemp(prefix="tgwrap-")
            try:
                self._clone_repo(repo=repo_url, target_dir=temp_dir)
                all_versions = get_all_versions(temp_dir)
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

            now = datetime.now(UTC)
            for version in versions:
                tag = version["tag"]
                if tag == self.latest_version:
                    version["release_date"] = "unknown"
                else:
                    release_date = all_versions.get(tag, {}).get("created_date")
                    version["release_date"] = release_date
                    if release_date:
                        version["days_since_release"] = (now - release_date).days

            self.printer.header(
                "Deployed versions:" if versions else "No deployed versions detected",
                print_line_before=True,
            )

            versions = sorted(versions, key=lambda x: x["path"])
            for version in versions:
                days_since_release = version.get("days_since_release", 0)
                message = f'-> {version["path"]}: {version["tag"]} (released {days_since_release} days ago)'
                if version["release_date"] == "unknown":
                    self.printer.normal(message)
                elif days_since_release > 120:
                    self.printer.error(message)
                elif days_since_release > 80:
                    self.printer.warning(message)
                elif days_since_release < 40:
                    self.printer.success(message)
                else:
                    self.printer.normal(message)

                if version.get("git_status"):
                    message = f'WARNING: git status: {version["git_status"].strip()}'
                    if "up to date" not in message:
                        self.printer.warning(message)

            self.printer.normal("\n")
            self.printer.warning(
                """
Note:
    This result only says something about the freshness of the deployed configurations,
    but not whether the actual resources are in sync with these.

    Check the drift of these configurations with the actual deployments by
    planning and analyzing the results.

    Also, it uses the locally checked out repositories, make sure these are pulled so that
    this reflects the most up to date situation!
                """,
                print_line_before=True,
                print_line_after=True,
            )

            if out:
                print(json.dumps(versions, indent=4, cls=DateTimeEncoder))

        except Exception as exc:  # pylint: disable=broad-except
            self.printer.error(f"Unexpected error: {exc}")
            if self.printer.print_verbose:
                raise
            sys.exit(1)

    # Internal helpers --------------------------------------------------

    def _clone_repo(
        self,
        *,
        repo,
        target_dir,
        version_tag=None,
        prompt_func=None,
    ):
        def get_tags(directory):
            cmd = "git fetch --tags"
            subprocess.run(
                shlex.split(cmd),
                check=True,
                cwd=directory,
                stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            )

            cmd = "git tag -l --sort=-committerdate"
            result = subprocess.run(
                shlex.split(cmd),
                text=True,
                check=True,
                cwd=directory,
                stdout=subprocess.PIPE,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            )
            self.printer.verbose(result)

            tags = [tag for tag in result.stdout.strip().split("\n") if tag]
            tags.insert(0, self.latest_version)
            return tags

        def check_version_tag(reference, working_dir):
            is_latest = reference == self.latest_version
            is_branch = False
            is_tag = False

            if not is_latest:
                quiet_mode = "" if self.printer.print_verbose else "--quiet"
                tag_command = (
                    f"git show-ref --verify {quiet_mode} refs/tags/{reference}"
                )
                tag_process = subprocess.run(
                    shlex.split(tag_command),
                    cwd=working_dir,
                    capture_output=True,
                    check=False,
                )
                is_tag = tag_process.returncode == 0
                self.printer.verbose(f"Check for tag: {tag_process}")

                if not is_tag:
                    branch_command = f"git switch {reference}"
                    branch_process = subprocess.run(
                        shlex.split(branch_command),
                        cwd=working_dir,
                        capture_output=True,
                        check=False,
                    )
                    is_branch = branch_process.returncode == 0
                    self.printer.verbose(f"Check for branch: {branch_process}")

            if is_latest:
                self.printer.verbose(
                    f"The given reference '{reference}' is the latest version."
                )
            elif is_branch:
                self.printer.verbose(f"The given reference '{reference}' is a branch.")
            elif is_tag:
                self.printer.verbose(f"The given reference '{reference}' is a tag.")
            else:
                msg = f"The given reference '{reference}' is neither latest, a branch nor a tag."
                self.printer.verbose(msg)
                raise ValueError(msg)

            return is_latest, is_branch, is_tag

        self.printer.verbose(f"Clone repo {repo}")
        cmd = f"git clone {repo} {target_dir}"
        rc = subprocess.run(
            shlex.split(cmd),
            check=True,
            stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
            stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
        )
        self.printer.verbose(rc)

        if not version_tag:
            tags = get_tags(target_dir)
            questions = [
                inquirer.List(
                    "version",
                    message="Which version do you want to deploy?",
                    choices=tags,
                ),
            ]
            if prompt_func:
                version_tag = prompt_func(questions)["version"]
            else:
                version_tag = inquirer.prompt(questions)["version"]

            self.printer.normal("")

        is_latest, is_branch, is_tag = check_version_tag(
            reference=version_tag,
            working_dir=target_dir,
        )

        self.printer.header(f"Fetch repo using reference {version_tag}")

        if is_latest:
            pass
        elif is_tag:
            cmd = f"git checkout -b source {version_tag}"
            rc = subprocess.run(
                shlex.split(cmd),
                cwd=target_dir,
                check=True,
                stdout=sys.stdout if self.printer.print_verbose else subprocess.DEVNULL,
                stderr=sys.stderr if self.printer.print_verbose else subprocess.DEVNULL,
            )
            self.printer.verbose(rc)
        elif is_branch:
            pass
        else:
            self.printer.error(
                f"Version tag {version_tag} seems neither a branch or a tag, cannot switch to it!"
            )

        return version_tag, is_branch, is_tag
