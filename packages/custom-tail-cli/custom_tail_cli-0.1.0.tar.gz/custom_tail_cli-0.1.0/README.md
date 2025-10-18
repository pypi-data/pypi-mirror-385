### 📜 Для проєкту `custom-tail` (`README.md`)

```markdown
# Custom Tail CLI (`ctail`)

[![PyPI version](https://badge.fury.io/py/custom-tail-cli.svg)](https://badge.fury.io/py/custom-tail-cli)
[![Build Status](https://github.com/bohdanfariyon/custom-tail/actions/workflows/publish.yml/badge.svg)](https://github.com/bohdanfariyon/custom-tail/actions)

A simple command-line utility written in Python to display the last few lines of a file, mimicking the basic functionality of the GNU `tail` command. This tool is built using the `click` library.

---

## 🚀 Features

* **Show Last Lines**: Display the last N lines of a file (10 by default).
* **Follow Mode**: Watch a file for changes and output new lines as they are added (`-f` option).
* **Custom Line Count**: Specify the exact number of lines to display.
* **Dockerized**: Comes with a `Dockerfile` for easy containerization.

---

## 📦 Installation

You can install the package directly from PyPI:

```bash
pip install custom-tail-cli
````

-----

## 🛠️ Usage

The main command is `ctail`. You must provide a file path.

### **Basic Usage**

Show the last 10 lines of `logfile.log`.

```bash
ctail logfile.log
```

### **Command Options**

  * **`-n, --lines <number>`**: Specify the number of lines to show.

    ```bash
    # Show the last 5 lines
    ctail -n 5 logfile.log
    ```

  * **`-f, --follow`**: "Follow" mode. The command will wait and display new lines as they are written to the file. This is useful for monitoring log files in real-time.

    ```bash
    ctail -f /var/log/syslog
    ```

    *(Press `Ctrl+C` to exit follow mode.)*

-----

## 🐳 Docker Usage

You can also build and run this tool as a Docker container.

1.  **Build the image:**

    ```bash
    docker build -t ctail-app .
    ```

2.  **Run the container:**

    To see the help message:

    ```bash
    docker run --rm ctail-app --help
    ```

    To view the tail of a file from your current directory, you need to mount it as a volume:

    ```bash
    # This command mounts the current directory to /data inside the container
    # and tells ctail to read the file /data/logfile.log
    docker run --rm -v "$(pwd)":/data ctail-app /data/logfile.log
    ```

    To use follow mode on a local file:

    ```bash
    docker run --rm -v "$(pwd)":/data ctail-app -f /data/logfile.log
    ```

-----
