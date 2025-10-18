from setuptools import setup, find_packages

setup(
    name='jack_social_checker',
    version='0.1.0',
    author='JACK',
    author_email='gsksvsksksj@gmail.com',
    description='A Python tool for checking if an email is linked to Snapchat, Twitter, or Instagram accounts.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
    ],
)

