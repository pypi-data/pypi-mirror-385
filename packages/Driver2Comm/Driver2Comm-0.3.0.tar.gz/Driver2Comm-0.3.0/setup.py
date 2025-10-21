from setuptools import setup, find_packages

VERSION = "0.3.0"
DESCRIPTION = ("A computational framework for associating cancer cell-intrinsic driver genes with "
               "-extrinsic cell-cell communication")
LONG_DESCRIPTION = ("For systematic investigation of the relationship between cancer cell-intrinsic and "
                    "-extrinsic factors, we develop a general computational framework, Driver2Comm, for "
                    "associating driver genes of cancer cells with CCC in the TME using single-cell "
                    "transcriptomics data.")

setup(
    name="Driver2Comm",
    version=VERSION,
    keywords=["scRNA-seq", "cell-cell communication", "cancer driver gene", "tumor microenvironment"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/plain",   # 传 PyPI 可读
    url="https://github.com/xierunzhi",
    author="Runzhi Xie, Junping Li, Yuxuan Hu*, Gao Lin*",
    author_email="rzxie1998@gmail.com",
    maintainer="Runzhi Xie",
    maintainer_email="rzxie1998@gmail.com",
    packages=find_packages(),                     # 确保 Driver2Comm/data 有 __init__.py
    include_package_data=True,
    package_data={
        # 两种写法，二选一：
        # 1) 指定子包
        "Driver2Comm.data": ["lrp_human.csv"],
        # 2) 或者把整个包下的 data/*.csv 都收进去（更通用）
        # "Driver2Comm": ["data/*.csv"],
    },
    python_requires=">=3.8",
    platforms="any",
    license="MIT Licence",
    install_requires=[
        "numpy",
        "pandas",
        "statsmodels",
        "networkx",
        "matplotlib",
        "scipy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
