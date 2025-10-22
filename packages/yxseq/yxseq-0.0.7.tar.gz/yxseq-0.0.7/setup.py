# coding utf8
import setuptools
from yxseq.versions import get_versions

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="yxseq",
    version=get_versions(),
    author="Yuxing Xu",
    author_email="xuyuxing@mail.kib.ac.cn",
    description="Xu Yuxing's personal tools for biology sequence analysis",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url="https://github.com/SouthernCD/yxseq",
    include_package_data = True,

    entry_points={
        "console_scripts": ["yxseq = yxseq.cli:main"]
    },    

    packages=setuptools.find_packages(),

    install_requires=[
        "yxutil",
        "yxmath",
        "yxsql",
        "numpy>=1.18.1",
        "pyfaidx>=0.5.5.2",
        "interlap>=0.2.6",
        "biopython<=1.80",
        "bcbio-gff>=0.6.6",
        "tables",
    ],

    python_requires='>=3.5',
)