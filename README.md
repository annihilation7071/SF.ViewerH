# SV.ViewerH
___
*Save your collection*

![](https://files.catbox.moe/ac0yk1.png)

### Features:
- View projects from **nhentai.net** downloaded using [nhentai][1].
- View projects from **hitomi.la**, **nhentai.net** (and other **sites** in the future) downloaded using [gallery-dl][2].
- Browser extension that allows you to easily download an open project page from supported sites.

### SV.ViewerH is a viewer for images uploaded via:
- [nhentai][1]
- [gallery-dl][2]

### Supports
| Site        | Supported downloader           | Chrome extension                         |
|-------------|--------------------------------|------------------------------------------|
| nhentai.net | [nhentai][1] / [gallery-dl][2] | supported([nhentai][1] / [gallery-dl][2] |
| hitomi.la   | [gallery-dl][2]                | supported([gallery-dl][2])               |

### Install and run:
#### Using system python
```bash
git clone [this repository]
cd SV.ViewerH
pip install -r requirements.txt
app.py
```
#### Using venv
```bash
git clone [this repository]
cd SV.ViewerH
python -m venv venv
./venv/scripts/activate
qpp.py
```
### How to start:
1. Upload files using [nhentai][1] or [gallery-dl][2]. (```--write-info-json``` parameter **MUST** be used for [gallery-dl][2])
2. Create a library settings file.
   + You can use the file ```./settings/libs/libs_example.json``` as a reference. You can simply copy it and rename it. All files matching the pattern ```libs_NAME.json``` will be read, except ```libs_example.json```.
   + Processor must be selected according to the downloader and the site.
     + ```nhentai``` or ```gallery-dl-nhentai``` for **nhentai.net**
     + ```gallery-dl-hitomila``` for **hitomi.la** 
3. Run **app.py**, the server IP address will appear in the terminal.

### Chrome-Extension
There is an extension for chromium-based browsers in the ```./extension directory```.
It can be installed via the browser extensions menu (*just **drag** the .crx into the extensions tab and click **install***). The extension simply downloads the open project to the library specified in ```./settings/download/download_targets.json``` (which must exist in ```./sittings/libs```).

*You can specify some additional downloader parameters by creating a ```config_nhentai.json```/```config_gallery-dl.json``` file in the ```./settings/download directory```, an example file is there under the name ```config_nhentai_example.json```/```config_gallery-dl_example.json```.*

[1]: https://github.com/RicterZ/nhentai
[2]: https://github.com/mikf/gallery-dl
