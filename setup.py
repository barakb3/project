from setuptools import find_packages, setup


setup(
    name="project",
    version="0.1.0",
    author="Barak Basson",
    description="First project.",
    packages=find_packages(),
    install_requires=["click", "flask"],
    entry_points={
        "console_scripts": [
            "client = :client",
            "server = :server",
        ],
    },
    tests_require=["pytest"],
)
