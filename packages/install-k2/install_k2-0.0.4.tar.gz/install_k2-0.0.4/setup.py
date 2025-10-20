from setuptools import setup


setup(
    name="install_k2",
    version="0.0.4",
    package_dir={"": "src"},
    description="Install k2 package",
    author="The Lattifai Development Team",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    install_requires=[
    ],
    entry_points={
        "console_scripts": [
            "install_k2=install_k2.install_k2:install_k2",
            "install-k2=install_k2.install_k2:install_k2",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
