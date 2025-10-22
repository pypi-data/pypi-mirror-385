import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unlock-processpool-win",
    version="2.2.0",
    author="Half open flowers",
    author_email="1816524875@qq.com",
    description="Unlock Windows process limit for ProcessPoolExecutor and joblib (61->508 workers)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JackLFH/unlock-processpool",
    packages=setuptools.find_packages(include=["unlock_processpool", "unlock_processpool.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[],
    include_package_data=True,
    license="BSD-3-Clause",
)