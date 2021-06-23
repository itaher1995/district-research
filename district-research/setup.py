import setuptools
import district_research

setuptools.setup(
    name="district-research",
    version=district_research.__version__,
    author="Ibrahim Yousuf Taher",
    author_email="ibrahim@brandnewcongress.com",
    description="Package to create data deliverables for district research",
    packages=(
        'district_research',
        'district_research.data'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'pandas', 'matplotlib', 'geopandas', 
        'numpy', 'bs4', 'requests'
    ]
)