from setuptools import setup, find_packages

setup(
    name='Mail_check_JACK',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'mail-check-jack = mail_check_jack.cli:main',
        ],
    },
    author='JACK',
    description='أداة لفحص البريد الإلكتروني',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
