from setuptools import setup, find_packages

setup(
    name='waii-sdk-py',
    version='1.0',
    description='Provides access to the Waii APIs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Waii, Inc.',
    url='http://www.waii.ai',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=[
        'requests', 'json', 'typing'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
