import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setuptools.setup(
    name="arlas_cli",
    entry_points={'console_scripts': ['arlas_cli=arlas.cli.cli:main']},
    version="26.6.4",
    author="Gisaïa",
    description="ARLAS Command line for ARLAS Management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.10',
    py_modules=["arlas.cli.arlas_cloud",
                "arlas.cli.cli",
                "arlas.cli.collections",
                "arlas.cli.configurations",
                "arlas.cli.iam",
                "arlas.cli.index",
                "arlas.cli.model_infering",
                "arlas.cli.org",
                "arlas.cli.persist",
                "arlas.cli.readers",
                "arlas.cli.service",
                "arlas.cli.settings",
                "arlas.cli.user",
                "arlas.cli.utils",
                "arlas.cli.variables"],
    package_dir={'': 'src'},
    install_requires=get_requirements()
)
