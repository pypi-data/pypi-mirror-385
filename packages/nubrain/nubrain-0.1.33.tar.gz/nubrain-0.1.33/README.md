# nubrain-connect

Create Pipfile (only when running for the first time):
```bash
conda create -y -n py-nubrain -c conda-forge pip setuptools pipenv python=3.12
cd /home/john/github/nubrain-connect
pipenv --rm
rm Pipfile Pipfile.lock
pipenv install -e ./app
pipenv install -e "./app[dev]" --dev
```

Update Pipfile (after modifying dependencies in `pyproject.toml` file):
```bash
cd /home/john/github/nubrain-connect
conda activate py-nubrain
pipenv lock --clear
```

For local testing:
```bash
# Not the `liblsl` dependency (needed by pylsls).
conda create -y -n py-nubrain -c conda-forge pip setuptools pipenv liblsl python=3.12
conda activate py-nubrain
pip install -e /home/john/github/nubrain-connect/app
```

## Run experiment

```bash
sudo nano /sys/bus/usb-serial/devices/ttyUSB0/latency_timer
# Change to 1

conda activate py-nubrain

nubrain --config=/path/to/example_config.yaml
```
