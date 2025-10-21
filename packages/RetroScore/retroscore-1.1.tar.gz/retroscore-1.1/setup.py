from setuptools import setup, find_packages

setup(
    name='RetroScore',
    version='1.1',
    packages=find_packages(),
    install_requires=[
        "rxnmapper==0.4.2",
        "numpy",
        "pandas",
        "rdkit",
        "torch",
        "torchaudio",
        "torchvision",
        "tqdm",
        "joblib",
        "py7zr",
        "zenodo-get"
    ],
    # package_dir={"": "RetroScore"},
    # packages=find_packages("RetroScore"),
    package_data={
        "RetroScore": [
            "data/multi_step/retro_data/dataset/stocks.7z",
            "data/multi_step/retro_data/saved_models/best_epoch_final_4.pt",
            "experiments/uspto_full/epoch_65.pt"
        ],
    },
    include_package_data=True,   # 同时接受 MANIFEST.in
    description='RetroScoreTools',
    author='SnowGao',
    author_email='892381602@qq.com',
)
