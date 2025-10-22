import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = []
with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires += [x.strip() for x in fobj.readlines() if x.strip()]

setup(
    name="django-static-adminlte",
    version="3.2.0.3",
    description="Django application contain adminlte static files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rRR0VrFP",
    maintainer="rRR0VrFP",
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django-static-adminlte"],
    packages=find_packages(".", exclude=[]),
    install_requires=requires,
    zip_safe=False,
    include_package_data=True,
)
