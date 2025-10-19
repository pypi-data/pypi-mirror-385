from setuptools import setup, find_packages

setup(
    name="meu_primeiro_pacote_exemplo",
    version="0.1.0",
    description="Um pacote de calculadora simples",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Seu Nome",
    author_email="marcos.luiz@gmx.us",
    url="https://github.com/Cempressa",
    packages=find_packages(),
    python_requires=">=3.6",
)
