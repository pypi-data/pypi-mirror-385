
from setuptools import setup, find_packages

setup(
    name="playwright_traceview_html",
    version="0.2.0",
    author="Jaya Krishna",
    author_email="jayakrishna107@gmail.com",
    description="Interactive local HTML report and server for Playwright trace results.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JK-JuLaYi/playwright-traceview-html",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "playwright>=1.45.0",
        "jinja2"
    ],
    entry_points={
        "console_scripts": [
            "playwright_traceview_html=trace_server.html_generator:main",
        ],
    },
    python_requires=">=3.11",
    license="MIT",
)
