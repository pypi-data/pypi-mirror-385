from setuptools import setup, find_packages

# Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Buscador_De_Cursos_by_Jhonatanhck_hack4u",
    version="0.5.0",
    packages=find_packages(),
    install_requires=[],
    author="Jhonatan Pimentel",
    description="Una biblioteca para consultar cursos de hack4u,",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
)
