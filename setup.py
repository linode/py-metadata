import os
from pathlib import Path

import setuptools

current_dir = Path(__file__).parent.resolve()
readme_path = current_dir / "README.md"
requirements_path = current_dir / "requirements.txt"

setuptools.setup(
    name="py-metadata",
    version="0.0.0",
    author="Linode",
    author_email="dev-dx@linode.com",
    description="A simple client to interact with the Linode Metadata service in Python.",
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    #keywords="ansible",
    url="https://github.com/linode/py-metadata/",
    packages=["metadata"],
   # install_requires=requirements_path.read_text().splitlines(),
    python_requires=">=3",
    #entry_points={
     #   "console_scripts": ["metadata=metadata.metadata_client:main"],
    #},
)