import hashlib
import os
import subprocess
import tempfile
from typing import List

from rich.syntax import Syntax

from autocoder_nano.edit.code.modification_ranker import CodeModificationRanker
from autocoder_nano.edit.text import TextSimilarity
from autocoder_nano.utils.git_utils import commit_changes
from autocoder_nano.core import AutoLLM
from autocoder_nano.core import prompt
from autocoder_nano.actypes import AutoCoderArgs, PathAndCode, MergeCodeWithoutEffect, CodeGenerateResult, \
    CommitResult
from autocoder_nano.utils.printer_utils import Printer


printer = Printer()
console = printer.get_console()
# console = Console()


def git_print_commit_info(commit_result: CommitResult):
    printer.print_table_compact(
        data=[
            ["Commit Hash", commit_result.commit_hash],
            ["Commit Message", commit_result.commit_message],
            ["Changed Files", "\n".join(commit_result.changed_files)]
        ],
        title="Commit 信息", headers=["Attribute", "Value"], caption="(Use /revert to revert this commit)"
    )

    if commit_result.diffs:
        for file, diff in commit_result.diffs.items():
            printer.print_text(f"File: {file}", style="green")
            syntax = Syntax(diff, "diff", theme="monokai", line_numbers=True)
            printer.print_panel(syntax, title="File Diff", center=True)


class CodeAutoMergeEditBlock:
    def __init__(self, args: AutoCoderArgs, llm: AutoLLM, fence_0: str = "```", fence_1: str = "```"):
        self.llm = llm
        self.llm.setup_default_model_name(args.code_model)
        self.args = args
        self.fence_0 = fence_0
        self.fence_1 = fence_1

    @staticmethod
    def run_pylint(code: str) -> tuple[bool, str]:
        """
        --disable=all 禁用所有 Pylint 的检查规则
        --enable=E0001,W0311,W0312 启用指定的 Pylint 检查规则,
        E0001：语法错误(Syntax Error),
        W0311：代码缩进使用了 Tab 而不是空格(Bad indentation)
        W0312：代码缩进不一致(Mixed indentation)
        :param code:
        :return:
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(
                ["pylint", "--disable=all", "--enable=E0001,W0311,W0312", temp_file_path,],
                capture_output=True,
                text=True,
                check=False,
            )
            os.unlink(temp_file_path)
            if result.returncode != 0:
                error_message = result.stdout.strip() or result.stderr.strip()
                printer.print_text(f"Pylint 检查代码失败: {error_message}", style="yellow")
                return False, error_message
            return True, ""
        except subprocess.CalledProcessError as e:
            error_message = f"运行 Pylint 时发生错误: {str(e)}"
            printer.print_text(error_message, style="red")
            os.unlink(temp_file_path)
            return False, error_message

    def parse_whole_text(self, text: str) -> List[PathAndCode]:
        """
        从文本中抽取如下格式代码(two_line_mode)：

        ```python
        ##File: /project/path/src/autocoder/index/index.py
        <<<<<<< SEARCH
        =======
        >>>>>>> REPLACE
        ```

        或者 (one_line_mode)

        ```python:/project/path/src/autocoder/index/index.py
        <<<<<<< SEARCH
        =======
        >>>>>>> REPLACE
        ```
        """
        HEAD = "<<<<<<< SEARCH"
        DIVIDER = "======="
        UPDATED = ">>>>>>> REPLACE"
        lines = text.split("\n")
        lines_len = len(lines)
        start_marker_count = 0
        block = []
        path_and_code_list = []
        # two_line_mode or one_line_mode
        current_editblock_mode = "two_line_mode"
        current_editblock_path = None

        def guard(_index):
            return _index + 1 < lines_len

        def start_marker(_line, _index):
            nonlocal current_editblock_mode
            nonlocal current_editblock_path
            if _line.startswith(self.fence_0) and guard(_index) and ":" in _line and lines[_index + 1].startswith(HEAD):
                current_editblock_mode = "one_line_mode"
                current_editblock_path = _line.split(":", 1)[1].strip()
                return True
            if _line.startswith(self.fence_0) and guard(_index) and lines[_index + 1].startswith("##File:"):
                current_editblock_mode = "two_line_mode"
                current_editblock_path = None
                return True
            return False

        def end_marker(_line, _index):
            return _line.startswith(self.fence_1) and UPDATED in lines[_index - 1]

        for index, line in enumerate(lines):
            if start_marker(line, index) and start_marker_count == 0:
                start_marker_count += 1
            elif end_marker(line, index) and start_marker_count == 1:
                start_marker_count -= 1
                if block:
                    if current_editblock_mode == "two_line_mode":
                        path = block[0].split(":", 1)[1].strip()
                        content = "\n".join(block[1:])
                    else:
                        path = current_editblock_path
                        content = "\n".join(block)
                    block = []
                    path_and_code_list.append(PathAndCode(path=path, content=content))
            elif start_marker_count > 0:
                block.append(line)

        return path_and_code_list

    def get_edits(self, content: str):
        edits = self.parse_whole_text(content)
        HEAD = "<<<<<<< SEARCH"
        DIVIDER = "======="
        UPDATED = ">>>>>>> REPLACE"
        result = []
        for edit in edits:
            heads = []
            updates = []
            c = edit.content
            in_head = False
            in_updated = False
            for line in c.splitlines():
                if line.strip() == HEAD:
                    in_head = True
                    continue
                if line.strip() == DIVIDER:
                    in_head = False
                    in_updated = True
                    continue
                if line.strip() == UPDATED:
                    in_head = False
                    in_updated = False
                    continue
                if in_head:
                    heads.append(line)
                if in_updated:
                    updates.append(line)
            result.append((edit.path, "\n".join(heads), "\n".join(updates)))
        return result

    @prompt()
    def git_require_msg(self, source_dir: str, error: str) -> str:
        """
        auto_merge only works for git repositories.

        Try to use git init in the source directory.

        ```shell
        cd {{ source_dir }}
        git init .
        ```

        Then try to run auto-coder again.
        Error: {{ error }}
        """

    def _merge_code_without_effect(self, content: str) -> MergeCodeWithoutEffect:
        """
        合并代码时不会产生任何副作用，例如 Git 操作、代码检查或文件写入。
        返回一个元组，包含：
        - 成功合并的代码块的列表，每个元素是一个 (file_path, new_content) 元组，
          其中 file_path 是文件路径，new_content 是合并后的新内容。
        - 合并失败的代码块的列表，每个元素是一个 (file_path, head, update) 元组，
          其中：file_path 是文件路径，head 是原始内容，update 是尝试合并的内容。
        """
        codes = self.get_edits(content)
        file_content_mapping = {}
        failed_blocks = []

        for block in codes:
            file_path, head, update = block
            if not os.path.exists(file_path):
                file_content_mapping[file_path] = update
            else:
                if file_path not in file_content_mapping:
                    with open(file_path, "r") as f:
                        temp = f.read()
                        file_content_mapping[file_path] = temp
                existing_content = file_content_mapping[file_path]

                # First try exact match
                new_content = (
                    existing_content.replace(head, update, 1)
                    if head
                    else existing_content + "\n" + update
                )

                # If exact match fails, try similarity match
                if new_content == existing_content and head:
                    similarity, best_window = TextSimilarity(
                        head, existing_content
                    ).get_best_matching_window()
                    if similarity > self.args.editblock_similarity:
                        new_content = existing_content.replace(
                            best_window, update, 1
                        )

                if new_content != existing_content:
                    file_content_mapping[file_path] = new_content
                else:
                    failed_blocks.append((file_path, head, update))
        return MergeCodeWithoutEffect(
            success_blocks=[(path, content) for path, content in file_content_mapping.items()],
            failed_blocks=failed_blocks
        )

    def choose_best_choice(self, generate_result: CodeGenerateResult) -> CodeGenerateResult:
        """ 选择最佳代码 """
        if len(generate_result.contents) == 1:  # 仅一份代码立即返回
            printer.print_text("仅有一个候选结果，跳过排序", style="green")
            return generate_result

        ranker = CodeModificationRanker(args=self.args, llm=self.llm)
        ranked_result = ranker.rank_modifications(generate_result)
        # 过滤掉包含失败块的内容
        for content, conversations in zip(ranked_result.contents, ranked_result.conversations):
            merge_result = self._merge_code_without_effect(content)
            if not merge_result.failed_blocks:
                return CodeGenerateResult(contents=[content], conversations=[conversations])
        # 如果所有内容都包含失败块，则返回第一个
        return CodeGenerateResult(contents=[ranked_result.contents[0]], conversations=[ranked_result.conversations[0]])

    def _merge_code(self, content: str, force_skip_git: bool = False):
        file_content = open(self.args.file).read()
        md5 = hashlib.md5(file_content.encode("utf-8")).hexdigest()
        file_name = os.path.basename(self.args.file)

        codes = self.get_edits(content)
        changes_to_make = []
        changes_made = False
        unmerged_blocks = []
        merged_blocks = []

        # First, check if there are any changes to be made
        file_content_mapping = {}
        for block in codes:
            file_path, head, update = block
            if not os.path.exists(file_path):
                changes_to_make.append((file_path, None, update))
                file_content_mapping[file_path] = update
                merged_blocks.append((file_path, "", update, 1))
                changes_made = True
            else:
                if file_path not in file_content_mapping:
                    with open(file_path, "r") as f:
                        temp = f.read()
                        file_content_mapping[file_path] = temp
                existing_content = file_content_mapping[file_path]
                new_content = (
                    existing_content.replace(head, update, 1)
                    if head
                    else existing_content + "\n" + update
                )
                if new_content != existing_content:
                    changes_to_make.append(
                        (file_path, existing_content, new_content))
                    file_content_mapping[file_path] = new_content
                    merged_blocks.append((file_path, head, update, 1))
                    changes_made = True
                else:
                    # If the SEARCH BLOCK is not found exactly, then try to use
                    # the similarity ratio to find the best matching block
                    similarity, best_window = TextSimilarity(head, existing_content).get_best_matching_window()
                    if similarity > self.args.editblock_similarity:  # 相似性比较
                        new_content = existing_content.replace(
                            best_window, update, 1)
                        if new_content != existing_content:
                            changes_to_make.append(
                                (file_path, existing_content, new_content)
                            )
                            file_content_mapping[file_path] = new_content
                            merged_blocks.append(
                                (file_path, head, update, similarity))
                            changes_made = True
                    else:
                        unmerged_blocks.append((file_path, head, update, similarity))

        if unmerged_blocks:
            if self.args.request_id and not self.args.skip_events:
                # collect unmerged blocks
                event_data = []
                for file_path, head, update, similarity in unmerged_blocks:
                    event_data.append(
                        {
                            "file_path": file_path,
                            "head": head,
                            "update": update,
                            "similarity": similarity,
                        }
                    )
                return
            printer.print_text(f"发现 {len(unmerged_blocks)} 个未合并的代码块，更改将不会应用，请手动检查这些代码块后重试.",
                               style="yellow")
            self._print_unmerged_blocks(unmerged_blocks)
            return

        # lint check
        for file_path, new_content in file_content_mapping.items():
            if file_path.endswith(".py"):
                pylint_passed, error_message = self.run_pylint(new_content)
                if not pylint_passed:
                    printer.print_text(
                        f"代码文件 {file_path} 的 Pylint 检查未通过，本次更改未应用。错误信息: {error_message}",
                        style="yellow")

        if changes_made and not force_skip_git and not self.args.skip_commit:
            try:
                commit_changes(self.args.source_dir, f"auto_coder_pre_{file_name}_{md5}")
            except Exception as e:
                printer.print_text(self.git_require_msg(source_dir=self.args.source_dir, error=str(e)), style="red")
                return
        # Now, apply the changes
        for file_path, new_content in file_content_mapping.items():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(new_content)

        if self.args.request_id and not self.args.skip_events:
            # collect modified files
            event_data = []
            for code in merged_blocks:
                file_path, head, update, similarity = code
                event_data.append(
                    {
                        "file_path": file_path,
                        "head": head,
                        "update": update,
                        "similarity": similarity,
                    }
                )

        if changes_made:
            if not force_skip_git and not self.args.skip_commit:
                try:
                    commit_result = commit_changes(self.args.source_dir, f"auto_coder_{file_name}_{md5}")
                    git_print_commit_info(commit_result=commit_result)
                except Exception as e:
                    printer.print_text(self.git_require_msg(source_dir=self.args.source_dir, error=str(e)),
                                       style="red")
            printer.print_text(
                f"已在 {len(file_content_mapping.keys())} 个文件中合并更改,完成 {len(changes_to_make)}/{len(codes)} 个代码块.",
                style="green"
            )
        else:
            printer.print_text("未对任何文件进行更改.", style="yellow")

    def merge_code(self, generate_result: CodeGenerateResult, force_skip_git: bool = False):
        result = self.choose_best_choice(generate_result)
        self._merge_code(result.contents[0], force_skip_git)
        return result

    @staticmethod
    def _print_unmerged_blocks(unmerged_blocks: List[tuple]):
        printer.print_text("未合并的代码块:", style="yellow")
        for file_path, head, update, similarity in unmerged_blocks:
            printer.print_text(f"文件: {file_path}", style="yellow")
            printer.print_text(f"搜索代码块(相似度：{similarity}):", style="yellow")
            syntax = Syntax(head, "python", theme="monokai", line_numbers=True)
            printer.print_panel(syntax)
            printer.print_text(f"替换代码块:", style="yellow")
            syntax = Syntax(update, "python", theme="monokai",
                            line_numbers=True)
            printer.print_panel(syntax)
        printer.print_text(f"未合并的代码块总数: {len(unmerged_blocks)}", style="yellow")