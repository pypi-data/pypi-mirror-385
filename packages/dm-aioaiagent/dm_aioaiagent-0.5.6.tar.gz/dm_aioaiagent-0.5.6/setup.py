from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='dm-aioaiagent',
    version='v0.5.6',
    author='dimka4621',
    author_email='mismartconfig@gmail.com',
    description='This is my custom aioaiagent client',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/dm-aioaiagent',
    packages=find_packages(),
    install_requires=[
        'dm-logger>=0.6.6, <0.7.0',
        'python-dotenv>=1.0.0, <1.1.0',
        'pydantic>=2.9.2, <3.0.0',
        'langchain>=0.3.0, <0.4.0',
        'langchain-core>=0.3.5, <0.4.0',
        'langchain-community>=0.3.0, <0.4.0',
        'langchain-openai>=0.3.0, <0.4.0',
        'langchain-anthropic>=0.3.0, <0.4.0',
        'langgraph>=0.3.23, <0.4.0',
        'langsmith>=0.3.45, <0.4.0',
        'grandalf>=0.8.0, <0.9.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='dm aioaiagent',
    project_urls={
        'GitHub': 'https://github.com/MykhLibs/dm-aioaiagent'
    },
    python_requires='>=3.9'
)
