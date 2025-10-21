from setuptools import setup
from pathlib import Path

# Read README
readme = Path(__file__).parent / "README.md"
long_description = readme.read_text(encoding='utf-8') if readme.exists() else ""

setup(
    name='verctrl',
    version='1.0.0',
    py_modules=['verctrl'],
    install_requires=[
        'PyQt6>=6.0.0',
        'lucide-py>=0.1.0',
    ],
    entry_points={
        'console_scripts': [
            'verctrl=verctrl:main',
        ],
    },
    author='REN',
    author_email='totallynotbedlessnoob@gmail.com',
    description='Lightweight version control CLI tool with smart file detection and PyQt6 GUI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ren/verctrl',
    project_urls={
        'Bug Reports': 'https://github.com/ren/verctrl/issues',
        'Source': 'https://github.com/ren/verctrl',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    keywords='version-control backup cli gui pyqt6',
)
