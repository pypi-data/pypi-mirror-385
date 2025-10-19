# Telegraphist
<div align="center">
Telegraphist is a TUI-based game made in Python which focuses on time, precision sending correct signals under pressure.

---

![game screeshot](image.png)

---

# Introduction
Telegraphist is a text-based game where you have to telegraph messages in a high pressure environment of war room during WW2... less time, almost no resources to send another signal. Each morse counts. What will you do?



### Made for <br> 
![Hack Club Badge](https://img.shields.io/badge/Hack%20Club-EC3750?logo=hackclub&logoColor=fff&style=for-the-badge)

### Built Using
![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge)

### Project Info
![GitHub License](https://img.shields.io/github/license/chishxd/telegraphist)
![GitHub last commit](https://img.shields.io/github/last-commit/chishxd/telegraphist)


</div>

## Installation

### Requirements

Python 3.10+

### Easy Installation
Clone the repository and open it.
Run the `run.sh` (on Linux/Mac) or `run.bat` (on Windows) to install the game!

> NOTE: Linux/Mac user would need to make the `run.sh` executable first
```sh
chmod +x run.sh
./run.sh
```

### Manual installation

1. Clone the repo
```bash
git clone https://github.com/chishxd/telegraphist.git
cd telegraphist
```

2. Initialize Virtual Environment (optional, but recommended)
```bash
python -m venv .venv
#On Linux/MacOS
source .venv/bin/activate
#On Windows
source .venv\bin\activate.bat

#Upgrade pip
pip install --upgrade pip


#Install Deps
pip install -r requirements.txt
```

## Usage

Just run the code!
```bash
python telegraphist.py
```

## Tech Stack

**Language** : Python
**Libraries** : rich, pyinput, playsound3


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)