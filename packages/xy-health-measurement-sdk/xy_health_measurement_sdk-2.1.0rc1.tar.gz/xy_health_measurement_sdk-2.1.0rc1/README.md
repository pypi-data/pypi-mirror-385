# 小阳心健康测量SDK

[使用手册](https://measurement.xymind.cn/docs/sdk/python.html)

## Conda
```bash
conda create --name measurement_client_sdk -y python=3.10 && conda activate measurement_client_sdk
pip install build toml twine
pip install -r <(python -c "import toml; print('\n'.join(toml.load('pyproject.toml')['project']['dependencies']))")
```

## publish
```bash
# clear
sudo rm -rf dist *.egg-info
# build
python -m build
# publish
python -m twine upload dist/*

# build docker image
docker build --build-arg ACCELERATE_CONFIG='--trusted-host packages.aliyun.com -i https://62629dda4e333f02816fb492:%284dbBWuBUHY8@packages.aliyun.com/62629ddec2b7347ce520e075/pypi/xy' -t xiaoyangtech/measurement-python-client-sdk:2.0.0rc15 .
docker build --build-arg ACCELERATE_CONFIG='--trusted-host packages.aliyun.com -i https://62629dda4e333f02816fb492:%284dbBWuBUHY8@packages.aliyun.com/62629ddec2b7347ce520e075/pypi/xy' -t registry.cn-shanghai.aliyuncs.com/measurement/python-client-sdk:2.0.0rc15 .
```