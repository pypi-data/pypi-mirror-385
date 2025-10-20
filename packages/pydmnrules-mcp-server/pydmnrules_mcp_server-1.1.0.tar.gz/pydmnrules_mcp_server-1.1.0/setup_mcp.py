import setuptools

with open('README_MCP.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pydmnrules-mcp-server',
    version='1.1.0',
    author='uengine (rickjang)',
    author_email='rick.jang@uengine.org',
    description='MCP server for pyDMNrules-enhanced - enables LLMs to execute DMN decision rules with DRD support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/uengine/pyDMNrules',
    packages=['pydmnrules_mcp'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'fastmcp>=0.4.0',
        'pydantic>=2.0.0',
        'aiofiles>=23.0.0',
        'pydmnrules-enhanced>=1.6.0',
    ],
    entry_points={
        'console_scripts': [
            'pydmnrules-mcp-server=pydmnrules_mcp.server:main',
        ],
    },
    keywords='dmn decision-model mcp model-context-protocol llm ai fastmcp claude',
    project_urls={
        'Documentation': 'https://github.com/uengine/pyDMNrules/blob/master/README_MCP.md',
        'Source': 'https://github.com/uengine/pyDMNrules',
        'Tracker': 'https://github.com/uengine/pyDMNrules/issues',
    },
)


