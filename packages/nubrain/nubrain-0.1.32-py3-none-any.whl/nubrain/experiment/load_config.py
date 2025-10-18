import os
from dataclasses import dataclass, field, fields
from typing import Dict, Optional, Union, get_args, get_origin

import yaml


@dataclass(frozen=True)
class EegExperimentConfig:
    """
    Validate configuration for EEG experiment.

    We do not use pydantic, because of the breaking changes introduced in pydantic 2 and
    the problems with dependency resolution for libraries that depend either on pydantic
    1 or 2. Pydantic is the path to dependency hell.

    Setting `frozen=True` makes instances immutable, to prevent accidental changes at
    runtime.
    """

    subject_id: str
    session_id: str

    output_directory: str
    image_directory: str

    utility_frequency: float

    # Timing parameters
    initial_rest_duration: float
    image_duration: float
    isi_duration: float
    isi_jitter: float
    inter_block_grey_duration: float

    # Experiment structure
    n_blocks: int
    images_per_block: int
    n_target_events: int

    response_window_duration: float

    device_type: str
    lsl_stream_name: Optional[str] = "DSI-24"

    eeg_device_address: Optional[str] = None

    # Use default_factory for mutable types
    eeg_channel_mapping: Optional[Dict[int, str]] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validation after the object has been initialized.
        """
        # Runtime type validation. Iterate over all fields defined in the dataclass.
        for f in fields(self):
            value = getattr(self, f.name)

            # Get the origin and args of the type hint
            origin = get_origin(f.type)
            args = get_args(f.type)

            # Check if this is an Optional type (Union with None)
            is_optional = origin is Union and len(args) == 2 and type(None) in args

            if is_optional:
                # For Optional types, get the non-None type
                actual_type = args[0] if args[1] is type(None) else args[1]

                # Allow None for Optional fields
                if value is None:
                    continue

                # If not None, check if it matches the expected type
                # Handle Dict specially
                if get_origin(actual_type) is dict:
                    if not isinstance(value, dict):
                        raise TypeError(
                            f"Invalid type for '{f.name}'. "
                            f"Expected dict or None, but got {type(value).__name__}."
                        )
                elif not isinstance(value, actual_type):
                    raise TypeError(
                        f"Invalid type for '{f.name}'. "
                        f"Expected {actual_type.__name__} or None, "
                        f"but got {type(value).__name__}."
                    )
            else:
                # For non-Optional types, use the original logic.
                check_type = origin or f.type

                # Special handling for Dict type.
                if origin is dict:
                    if not isinstance(value, dict):
                        raise TypeError(
                            f"Invalid type for '{f.name}'. "
                            f"Expected dict, but got {type(value).__name__}."
                        )
                elif not isinstance(value, check_type):
                    raise TypeError(
                        f"Invalid type for '{f.name}'. "
                        f"Expected {check_type.__name__}, but got {type(value).__name__}."
                    )

        # The loop above checked that `eeg_channel_mapping` is a dict. Now we check the
        # contents of the dict (only if it's not empty).
        if self.eeg_channel_mapping:
            if not all(isinstance(k, int) for k in self.eeg_channel_mapping.keys()):
                raise TypeError("All keys in 'eeg_channel_mapping' must be integers.")

            if not all(isinstance(v, str) for v in self.eeg_channel_mapping.values()):
                raise TypeError("All values in 'eeg_channel_mapping' must be strings.")

        # Validate device_type.
        valid_devices = ["cyton", "dsi24", "synthetic"]
        if self.device_type not in valid_devices:
            raise ValueError(
                f"device_type must be one of {valid_devices}, got {self.device_type}"
            )

        if self.device_type == "synthetic":
            print("WARNING: USING SYNTHETIC DEVICE (DEMO MODE)")

        # Validate that eeg_device_address is provided for Cyton device.
        if self.device_type == "cyton" and not self.eeg_device_address:
            raise ValueError(
                "eeg_device_address must be provided when using Cyton device"
            )

        # Ensure that the response window (in which the participant to an attention task
        # target event counts as a hit) end before the next trial.
        if (self.image_duration + self.isi_duration) < self.response_window_duration:
            raise ValueError("Response window is longer than trial duration")

        # Introduce an (arbitrary) upper limit to the number of target events:
        if (self.n_blocks * self.images_per_block * 0.5) <= self.n_target_events:
            ValueError("Too many target events")
        elif self.n_target_events < 0:
            ValueError("Negativ number of target events")

        print("Configuration successfully loaded and validated.")


def load_config_yaml(*, yaml_file_path: str):
    """
    Load yaml file with settings for nubrain EEG experiment.
    """
    if not os.path.isfile(yaml_file_path):
        raise AssertionError(f"Config file not found: {yaml_file_path}")

    with open(yaml_file_path, "r") as file:
        config_dict = yaml.safe_load(file)

    # Ensure optional fields are present in the dict with None if not specified.
    if "eeg_device_address" not in config_dict:
        config_dict["eeg_device_address"] = None

    if "eeg_channel_mapping" not in config_dict:
        config_dict["eeg_channel_mapping"] = None

    if "lsl_stream_name" not in config_dict:
        config_dict["lsl_stream_name"] = "DSI-24"  # Use default

    # Validate config.
    config_dataclass = EegExperimentConfig(**config_dict)

    return config_dict
