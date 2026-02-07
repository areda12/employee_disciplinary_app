from setuptools import setup, find_packages

def get_requirements():
    try:
        with open("requirements.txt") as f:
            return [r for r in f.read().splitlines() if r.strip()]
    except FileNotFoundError:
        return []

setup(
    name="employee_disciplinary_app",
    version="0.0.1",
    description="Employee Disciplinary Action Report for ERPNext",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=get_requirements(),
)
