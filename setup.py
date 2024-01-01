from setuptools import setup, find_packages


setup(
    name='project',
    version='0.1.0',
    author='Barak Basson',
    description='First project.',
    packages=find_packages(),
    install_requires=['click', 'flask'],
    entry_points={
        'console_scripts': [
            'run_server = :run_server'
            'run_webserver = :run_webserver'
            'upload_thought = :upload_thought'
        ],
    },
    tests_require=['pytest'],
)
