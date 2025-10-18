from setuptools import setup, find_packages

setup(
    name="easyappmaker",                   # package name
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15",
        "playsound>=1.2.2"
    ],
    include_package_data=True,
    description="Personal Python apps: alarmapp, browserapp, and more.",
    author="Jay Barua",
    python_requires='>=3.10'
)
