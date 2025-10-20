from setuptools import setup, find_packages

setup(
    name='recipe_lib',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires='>=3.8',
    url='https://github.com/eldar/recipe_lib',
    author='Eldar Eliyev',
    author_email='eldar@example.com',
    description='A Python library to manage and explore recipes',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
