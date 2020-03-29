from setuptools import setup, find_packages

setup(
    name='mkdocs-plantuml-markdown-plugin',
    version='0.0.3',
    description='An MkDocs plugin to inject images in MkDocs markdown files',
    long_description='',
    keywords='mkdocs plantuml uml',
    url='https://github.com/michael72/mkdocs_plantuml_markdown',
    author='Michael Schulte',
    license='MIT',
    python_requires='>=3.7',
    install_requires=[
        'mkdocs>=1.1', 'httplib2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Documentation',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'plantuml_markdown = mkdocs_plantuml_markdown.plantuml_markdown_plugin:PlantUmlMarkdown'
        ]
    }
)