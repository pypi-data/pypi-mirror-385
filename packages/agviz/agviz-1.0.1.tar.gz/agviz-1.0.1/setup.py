from setuptools import setup, find_packages

setup(
    name="agviz",
    version="1.0.1",
    description="AutoGrad Visualizer (agviz): Visualize dependencies between states/parameters in autograd tree.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="James Hazelden",
    url="https://github.com/meeree/agviz",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'graphviz',
        'networkx'
    ],
    python_requires=">=3.2",
)
