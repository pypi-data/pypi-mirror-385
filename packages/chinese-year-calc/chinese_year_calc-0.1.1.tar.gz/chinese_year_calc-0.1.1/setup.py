from setuptools import setup, find_packages

setup(
    name = "chinese_year_calc",
    version = "0.1.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires = [],
    python_requires = ">=3.6",
    author = "xystudio",
    author_email = "173288240@qq.com",
    description = "中国纪年计算器",
    long_description = open("README.md",encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license = "MIT",
    url = "https://github.com/xystudio889/chinese-year-calc",
    entry_points = {
        "console_scripts": [
            "chyear = chyear.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords = "",
)
