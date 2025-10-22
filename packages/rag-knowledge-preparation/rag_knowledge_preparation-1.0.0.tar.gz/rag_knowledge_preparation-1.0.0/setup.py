"""
RAG Knowledge Preparation in Python
----------------------

Links
`````

* `development version <https://bitbucket.org/entinco/eic-aimodelknowledge-utils/src/main/lib-ragknowledgepreparation-python>`

"""

from setuptools import find_packages
from setuptools import setup

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='rag_knowledge_preparation',
    version='1.0.0',
    url='https://bitbucket.org/entinco/eic-aimodelknowledge-utils/src/master/lib-ragknowledgepreparation-python',
    license='Commercial',
    author='Enterprise Innovation Consulting LLC',
    author_email='seroukhov@entinco.com',
    description='RAG Knowledge Preparation in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'tests']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'pytest',
        'requests>=2.27.1, <3.0.0',
        'urllib3>=1.26.8, <2.0.0',
        'docling>=1.3.0',
        'tiktoken>=0.5.0',
        'pathspec>=0.11.0',
        'tree-sitter>=0.20.0',
        'tree-sitter-python>=0.20.0',
        'tree-sitter-javascript>=0.20.0',
        'tree-sitter-typescript>=0.20.0',
        'pygments>=2.15.0',
        'pydantic>=2.0.0',
        'chardet>=5.0.0',
        'google-generativeai>=0.3.0',
        'pip-services4-commons>=0.0.0',
        'pip-services4-components>=0.0.0',
        'pip-services4-config>=0.0.0',
        'pip-services4-data>=0.0.0',
        'pip-services4-http>=0.0.0',
        'pip-services4-mongodb>=0.0.0',
        'pip-services4-persistence>=0.0.0',
        'pip-services4-prometheus>=0.0.0',
        'pip-services4-rpc>=0.0.0',
        'pip-services4-swagger>=0.0.0'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
