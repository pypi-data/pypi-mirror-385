from setuptools import setup, find_packages

setup(
    name='vallaipallam',
    version='1.0.1',
    author='J. Nishanth Raj',
    author_email='jpnishanthraj@email.com',
    description='A Regional-based programming language and interpreter',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/NishanthRaj707',
    packages=['vallaipallam'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: Tamil',
    ],
    install_requires=[
        "requests",
        "psutil",
        "socket",
        "tkinter",
        "subprocess",
        "google-genai",
        "concurrent",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'vallaipallam = vallaipallam.shell:main'  # Adjust to your CLI entry
        ]
    },
    include_package_data=True,
)
