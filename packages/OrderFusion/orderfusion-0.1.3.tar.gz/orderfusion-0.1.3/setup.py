from setuptools import setup, find_packages

setup(
    name="OrderFusion",
    version="0.1.3",
    author="Runyao Yu",
    author_email="runyao.yu@tudelft.nl",
    description="Tutorial for the paper: OrderFusion Encoding Orderbook for End-to-End Probabilistic Intraday Electricity Price Forecasting",
    packages=find_packages(),
    install_requires=[
        "Pillow==10.4.0",
        "imageio==2.26.0",
        "ipython==8.10.0",
        "joblib==1.4.2",
        "matplotlib==3.7.0",
        "natsort==8.4.0",
        "numpy==1.26.4",
        "pandas==2.2.2",
        "scikit-learn==1.5.2",
        "tensorflow==2.16.2",
        "tqdm==4.66.5"
    ],
    python_requires=">=3.10,<3.12",
    license="MIT",
    url="https://huggingface.co/RunyaoYu",
)
