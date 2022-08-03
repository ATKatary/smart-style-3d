pip install trimesh==3.9.33 einops==0.3.2 scipy==1.5.2 siren-pytorch==0.1.5 usd-core==21.8 torch==1.9.0 torchtext==0.10.0 torchvision==0.10.0 cython==0.29.20 git+https://github.com/openai/CLIP.git@04f4dc2ca1ed0acc9893bd1a3b526a7e02c4bb10
git clone --recursive https://github.com/NVIDIAGameWorks/kaolin
cd kaolin
git checkout v0.10.0
python setup.py develop
cd ..

Green='\033[0;32m'
printf "${Green}Successfully completed setup!\033[0m"