<p align="center">
  <img src="https://constellab.space/assets/fl-logo/constellab-logo-text-white.svg" alt="Constellab Logo" width="80%">
</p>

<br/>

# 👋 Welcome to Glab 

```glab``` is a [Constellab](https://constellab.io) container developped by [Gencovery](https://gencovery.com/). It installs the Constellab bricks in the lab and then runs the python api.

## 🚀 What is Constellab?


✨ [Gencovery](https://gencovery.com/) is a software company that offers [Constellab](https://constellab.io)., the leading open and secure digital infrastructure designed to consolidate data and unlock its full potential in the life sciences industry. Gencovery's mission is to provide universal access to data to enhance people's health and well-being.

🌍 With our Fair Open Access offer, you can use Constellab for free. [Sign up here](https://constellab.space/). Find more information about the Open Access offer here (link to be defined).


## ✅ Features

This container is installed and runned by the [lab-manager](https://hub.docker.com/r/constellab/lab-manager). It installs the bricks of the data lab, then run the api. 
 

To view more information about the lab architecture [here](https://constellab.community/bricks/gws_core/latest/doc/architecture/7a8ec82f-f9d3-4f22-98cc-ee604a0e6b07) 

## 📄 Documentation

📄  For `gws_core` brick documentation, click [here](https://constellab.community/bricks/gws_core/latest/doc/getting-started/6efb7ab9-8508-4f99-b3e1-1a43e55755c4)

💫 For Constellab application documentation, click [here](https://constellab.community/bricks/gws_academy/latest/doc/getting-started/b38e4929-2e4f-469c-b47b-f9921a3d4c74)

## 🛠️ Installation

To run this container, you need to run the [lab-manager](https://hub.docker.com/r/constellab/lab-manager) container first. 

Then from [Constellab](https://constellab.space) space, you can configure your lab and run the glab.

## 🧪 Run modes

The container picks what to run after `init_all` based on the `RUN_MODE` env var:

| `RUN_MODE` | Command |
|------------|---------|
| `server` (default) | `gws server run --settings-path /lab/.sys/app/settings.json` |
| `test` | `gws server <test-parallel\|test> all --brick-name "${TEST_BRICK_NAME}"` |

In `test` mode:

- `TEST_BRICK_NAME` — brick whose tests are run (required).
- `TEST_PARALLEL` — `true` (default) uses `test-parallel`; `false` uses `test` for single-threaded execution.

The container exits with the test command's exit code — suitable for CI fan-out across bricks. A MariaDB instance must be reachable via the brick's usual `GWS_TEST_DB_*` env vars; the image does not provision it.

## 🤗 Community

🌍 Join the Constellab community [here](https://constellab.community/) to share and explore stories, code snippets and bricks with other users.

🚩 Feel free to open an issue if you have any question or suggestion.

☎️ If you have any questions or suggestions, please feel free to contact us through our website: [Constellab](https://constellab.io/).

## 🌎 License

```glab``` is completely free and open-source and licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

<br/>


This brick is maintained with ❤️ by [Gencovery](https://gencovery.com/).

<p align="center">
  <img src="https://framerusercontent.com/images/Z4C5QHyqu5dmwnH32UEV2DoAEEo.png?scale-down-to=512" alt="Gencovery Logo"  width="30%">
</p>