from setuptools import setup, find_packages

setup(
        name="booking_agent",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
)
