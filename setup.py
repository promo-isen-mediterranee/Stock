import io

from setuptools import find_packages
from setuptools import setup

setup(
    name="Stock API",
    version="1.0.0",
    license="restricted",
    maintainer="IMS Promo Team",
    maintainer_email="imspromo@yncrea.fr",
    description="Stock API for Promo IMS system",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
    extras_require={"test": ["pytest","coverage"]},
)