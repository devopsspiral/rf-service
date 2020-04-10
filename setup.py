import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rf-service",
    version="0.2.0",
    author="Michał Wcisło",
    author_email="mwcislo999@gmail.com",
    description="Robot Framework service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devopsspiral/rf-service",
    license="MIT",
    packages=["rf_runner"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
    ],
    keywords="robotframework testing test automation",
    python_requires='>=3.6',
    package_dir={'': 'src'},
    scripts=['src/scripts/rf-service'],
    install_requires=[
        'robotframework',
        'datetime',
        'requests',
        'flask',
        'flask-cors',
        'gevent'
    ],
)
