import unittest
import os
import sys
import importlib.util
import shutil
import subprocess

utilpath = os.path.dirname(os.path.abspath(__file__))
utilpath = os.path.join(utilpath, '..', 'util')
sys.path.append(utilpath)

pre_commit_scripts = os.path.dirname(os.path.abspath(__file__))
pre_commit_scripts = os.path.join(pre_commit_scripts, '..', 'pre-commit-scripts')
sys.path.append(pre_commit_scripts)

moduleName = '07-Compatible_Copyright_Update'
spec = importlib.util.spec_from_file_location(moduleName, os.path.join(pre_commit_scripts, '07-Compatible_Copyright_Update.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def with_env(workspace=None, git_project=None, commands=None):
    def decorate_function(func):
        def wrapper(*args, **kwargs):
            if workspace is None:
                raise RuntimeError("input workspace could not be None")

            if git_project is None:
                raise RuntimeError("test git_project can not be None")

            current_dir = os.getcwd()
            workspace_path = os.path.join(current_dir, workspace)

            if not os.path.exists(workspace_path):
                os.makedirs(workspace_path)
                print("create dir %s" % workspace_path)

            os.chdir(workspace_path)
            print("work dir changed to %s" % workspace_path)
            git_project_path = None
            try:
                for line in subprocess.check_output(["git", "clone", git_project]).splitlines():
                    print(line)
                dirs = os.listdir(workspace_path)
                for dir in dirs:
                    if dir in git_project:
                        git_project_path = os.path.join(workspace_path, dir)
                        break
                if git_project_path is not None:
                    os.chdir(git_project_path)
                    print("work dir changed to %s" % git_project_path)

                if commands is not None:
                    for command in commands:
                        for line in subprocess.check_output(command).splitlines():
                            print(line)
                return func(*args, **kwargs)
            except Exception as ex:
                print(ex)
            finally:
                os.chdir(workspace_path)
                os.chdir(current_dir)
                if git_project_path is not None:
                    shutil.rmtree(git_project_path)
                    print("clean dir %s" % git_project_path)

                os.chdir(current_dir)
                print("work dir changed to %s" % current_dir)
                shutil.rmtree(workspace_path)
                print("clean dir %s" % workspace_path)

        return wrapper
    return decorate_function


class TestCompatibleCopyrightUpdate(unittest.TestCase):

    def test_class_instance(self):
        hook_class = mod.hook()
        self.assertEqual(isinstance(hook_class, object), True)

    def test_logger_false(self):
        hook_class = mod.hook()
        hook_class.config_logger("Debug")
        self.assertEqual(str(hook_class.logger), "<Logger 07-Compatible_Copyright_Update.py (WARNING)>")

    def test_logger_true(self):
        hook_class = mod.hook()
        hook_class.config_logger("debug")
        self.assertEqual(str(hook_class.logger), "<Logger 07-Compatible_Copyright_Update.py (DEBUG)>")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "test_copyright_ok.py", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test python file with right copyright header"],
                        ["move", "../test_copyright_ok.py", "./"],
                        ["git", "add", "."]])
    def test_run_check_return_ok(self):
        hook_class = mod.hook()
        result = hook_class.run("hook_class")
        self.assertEqual(result, True, "It should be True")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "test_copyright_oneline_ok.py", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test python file with right copyright header"],
                        ["move", "../test_copyright_oneline_ok.py", "./"],
                        ["git", "add", "."]])
    def test_run_check_oneline_header_return_ok(self):
        hook_class = mod.hook()
        result = hook_class.run("hook_class")
        self.assertEqual(result, True, "It should be True")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "test_copyright_no_copyright.py", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test python file with no copyright header"],
                        ["move", "../test_copyright_no_copyright.py", "./"],
                        ["git", "add", "."]])
    def test_run_check_no_copyright_header_return_ok(self):
        hook_class = mod.hook()
        result = hook_class.run("hook_class")
        self.assertEqual(result, True, "It should be True")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "test_copyright_failed.py", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test python file with wrong copyright header"],
                        ["move", "../test_copyright_failed.py", "./"],
                        ["git", "add", "."]])
    def test_run_check_wrong_copyrighter_header_return_failed(self):
        hook_class = mod.hook()
        result = hook_class.run("hook_class")
        self.assertEqual(result, False, "It should be False")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "readme.md", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test readme.md"],
                        ["move", "../readme.md", "./"],
                        ["git", "add", "."]])
    def test_run_check_no_support_file_return_ok(self):
        hook_class = mod.hook()
        result = hook_class.run("hook_class")
        self.assertEqual(result, True, "It should be True")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "test_copyright_oneline_ok.py", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test python file with right copyright header"],
                        ["move", "../test_copyright_oneline_ok.py", "./"],
                        ["git", "add", "."]])
    def test_run_check_wrong_arg(self):
        hook_class = mod.hook()
        hook_class.run("hook_class")
        self.assertEqual(str(hook_class.logger), "<Logger 07-Compatible_Copyright_Update.py (WARNING)>")

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["move", "test_copyright_oneline_ok.py", "../"],
                        ["git", "add", "."],
                        ["git", "commit", "-m", "test python file with right copyright header"],
                        ["move", "../test_copyright_oneline_ok.py", "./"],
                        ["git", "add", "."]])
    def test_run_check_arg(self):
        hook_class = mod.hook()
        hook_class.run("debug")
        self.assertEqual(str(hook_class.logger), "<Logger 07-Compatible_Copyright_Update.py (WARNING)>")


if __name__ == '__main__':
    unittest.main()

