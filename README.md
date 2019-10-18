# C-GEM Blind Challenge Dashboard

Browse and download contents of Blind Challenge Shared Drives, with access by a 
password.


## Setup instructions

### Python package dependencies

The code in this repository assumes a Python 3 environment. 

You can replicate the environment used to run the C-GEM Blind Challenge 
Dashboard by using `conda` to install the virtual environment specified by 
the supplied environment files.

- `environment.lock.yaml` specifies all precise version numbers.
- `environment.yaml` specifies packages without version numbers. (Note that 
 a version number has been specified for `numpy`, as later versions were not 
 working on our server.)

With a Conda distribution installed, you can create a virtual environment as
follows:

```bash
conda env create -n blind -f environment.lock.yaml
```

### env files

The env files specifies configuration detail that is not suitable for hard-coding. 
A demo env files, `.env.demo` has been provided, which you should update and 
rename to `.env` (or `.env.dev`). 

The env file is used to specify:
- The path to the app-specific python environment (includes bin and lib subdirectories).
- GSuite credentials data
- the GSuite Shared Drive alphanumeric IDs, and names for display
- a password for access.

`.env_demo`:
```bash
PY_HOME=/path/to/python/environment/dir
SERVICE_ACCOUNT_FILE=/path/to/service-account.json
CREDENTIALS_AS_USER=username@example.com
CHALLENGE_NAME="Blind Challenge"
DRIVE_ID_A=xxxxxxxxxxxxxxxxx
DRIVE_ID_B=yyyyyyyyyyyyyyyyyyy
DRIVE_NAME_A=Name_A
DRIVE_NAME_B=Name_B
SHARED_PSWD="memorable safe password"
```


### Running the app

The app can be served by running the `start_blind.sh` script 
(or `start_blind_dev.sh` for development). It uses the `flask` executable to 
serve the app on the port specified in your .env file (or port 5111 if not 
provided). If you use the default port, the app will be accessible from your 
browser at `http://localhost:5111`.
