from setuptools import setup

setup(
    # The package name along with all the other metadata is specified in setup.cfg
    # However, GitHub's dependency graph can't see the package unless we put this here.
    name="tskit_arg_visualizer",
    packages=["tskit_arg_visualizer"],
)