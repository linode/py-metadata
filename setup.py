from pathlib import Path

import setuptools

current_dir = Path(__file__).parent.resolve()
readme_path = current_dir / "README.md"

setuptools.setup(
    name="py-metadata",
    version="0.0.0",
    author="Linode",
    author_email="dev-dx@linode.com",
    description="A simple client to interact with the Linode Metadata service in Python.",
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    url="https://github.com/linode/py-metadata/",
    packages=["metadata"],
    python_requires=">=3",

    install_requires=[
        "requests"
    ],
)