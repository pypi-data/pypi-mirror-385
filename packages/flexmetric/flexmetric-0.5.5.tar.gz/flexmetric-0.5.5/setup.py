from setuptools import setup, find_packages

setup(
    name="flexmetric",
    version="0.5.5",
    author="Nikhil Lingadhal",
    author_email="nikhillingadhal1999@gmail.com",
    description="A secure flexible Prometheus exporter for commands, databases, functions.",
    keywords="prometheus, monitoring, metrics, exporter, database, commands, flask",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nikhillingadhal1999/flexmetric",
    project_urls={
        "Homepage": "https://github.com/nikhillingadhal1999", 
        "Source": "https://github.com/nikhillingadhal1999/flexmetric",
        "Tracker": "https://github.com/nikhillingadhal1999/flexmetric/issues",
    },
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "prometheus_client>=0.16.0",
        "PyYAML>=6.0",
        "psutil>=5.8.0",
        "flask>=2.0.0",
        "clickhouse-connect>=0.6.0",
        "psycopg2-binary>=2.9.0",
        "ollama>=0.1.0"
    ],
    entry_points={
        "console_scripts": [
            "flexmetric = flexmetric.metric_process.prometheus_agent:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.7",
)
