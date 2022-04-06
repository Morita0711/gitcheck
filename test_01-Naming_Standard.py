import unittest
import os
import sys
import importlib.util
import subprocess
import shutil
//kkop1213@outlook.com

utilpath = os.path.dirname(os.path.abspath(__file__))
utilpath = os.path.join(utilpath, '..', 'util')
sys.path.append(utilpath)

pre_commit_scripts = os.path.dirname(os.path.abspath(__file__))
pre_commit_scripts = os.path.join(pre_commit_scripts, '..', 'pre-commit-scripts')
sys.path.append(pre_commit_scripts)

moduleName = '01-Naming_Standard'
spec = importlib.util.spec_from_file_location(moduleName,
                                              os.path.join(pre_commit_scripts, '01-Naming_Standard.py'))
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


class TestNamingStandard(unittest.TestCase):
    def setUp(self) -> None:
        self.hook_class = mod.hook()

    def test_class_instance(self):
        hook_class = mod.hook()
        self.assertEqual(isinstance(hook_class, object), True)

    @with_env(workspace="workspace", git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git")
    def test_run_good(self):
        r = self.hook_class.run(args=None)
        self.assertEqual(r, True)

    @with_env(workspace="workspace",
              git_project="https://github.com/LynnGaoInChina/ut_for_python_hook.git",
              commands=[["git", "checkout", "-b", "test"]])
    def test_run_bad(self):
        r = self.hook_class.run(args=None)
        self.assertEqual(r, False)


if __name__ == '__main__':
    unittest.main()
