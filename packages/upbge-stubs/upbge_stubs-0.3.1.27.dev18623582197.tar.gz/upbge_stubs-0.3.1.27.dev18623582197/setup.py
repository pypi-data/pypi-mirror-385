import glob
import os

from setuptools import setup

app_name = "upbge"
app_version = "0.3.1"
build_number = "18623582197"

module_version = "0.2.7"

name = f"{app_name.lower()}-stubs"

module_version = str(sum([int(n) * 10 ** (2 - i) for i, n in enumerate(module_version.split("."))]))

if build_number and not build_number.startswith("#"):
    version = "".join((".".join((app_version, module_version)), "dev", build_number))
else:
    version = ".".join((app_version, module_version))

files = glob.glob("**/__init__.pyi", recursive=True)
packages = set(map(lambda f: f.split(os.sep)[0].replace(".pyi", ""), files))
package_data = {pkg: ["py.typed", "*.pyi", "**/*.pyi"] for pkg in packages}

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=name,
    version=version,
    author="Xavier Cho",
    author_email="mysticfallband@gmail.com",
    description="API stubs for Blender and UPBGE generated with bpystubgen.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mysticfall/bpystubgen",
    packages=packages,
    package_data=package_data,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Text Editors :: Integrated Development Environments (IDE)"
    ]
)
