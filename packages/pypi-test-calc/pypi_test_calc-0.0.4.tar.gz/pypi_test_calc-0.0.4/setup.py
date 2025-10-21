from setuptools import setup, find_packages

setup(
    name='your_package',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
    ],
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your_package',
    author='Your Name',
    author_email='your.email@example.com',
    license='MIT',
)