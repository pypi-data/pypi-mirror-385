from pathlib import Path
from xdg_base_dirs import xdg_config_home, xdg_state_home

# Default locations for ssm-cli files
# ~/.config/ssm-cli/ssm.yaml
# ~/.config/ssm-cli/hostkey.pem
# ~/.local/state/ssm-cli/ssm.log

def get_conf_root(check=True) -> Path:
    root = xdg_config_home() / 'ssm-cli'
    if check and not root.exists():
        raise EnvironmentError(f"{root} missing, run `ssm setup` to create")
    return root

def get_state_root() -> Path:
    path = xdg_state_home() / 'ssm-cli'
    if not path.exists():
        path.mkdir(parents=True)
    return path

def get_conf_file(check=True) -> Path:
    path = get_conf_root(check) / 'ssm.yaml'
    if check and not path.exists():
        raise EnvironmentError(f"{path} missing, run `ssm setup` to create")
    return path

def get_log_file() -> Path:
    path = get_state_root() / 'run.log'
    return path

def get_ssh_hostkey(check=True) -> Path:
    path = get_conf_root(check) / 'hostkey.pem'
    if check and not path.exists():
        raise EnvironmentError(f"{path} missing, run `ssm setup` to create")
    return path
