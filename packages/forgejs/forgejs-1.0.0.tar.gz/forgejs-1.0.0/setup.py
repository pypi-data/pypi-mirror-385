from setuptools import setup, find_packages

setup(
    name="forgejs",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "forgejs=forgejs.cli:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.7",
    description="ForgeJS CLI para scaffolding de proyectos JavaScript/TypeScript",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BenjaMorenoo/ForgeJS-Templates",
    author="DonHuea",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
