# SV.ViewerH
___
*Save your collection*

### SV.ViewerH is a viewer for images uploaded via:
- [nhentai](https://github.com/RicterZ/nhentai)
- [gallery-dl](https://github.com/mikf/gallery-dl)

### Supports
| Site        | Supported downloader | Chrome extension   |
|-------------|----------------------|--------------------|
| nhentai.net | nhentai              | supported(nhentai) |
| hitomi.la   | gallery-dl           | coming soon        |

### Install and run:
```bash
git clone [this repository]
cd SV.ViewerH
pip install -r requirements.txt
app.py
```

### How to start:
1. Upload files using **nhentai** or **gallery-dl**. (```--write-info-json``` parameter **MUST** be used for **gallery-dl**)
2. Create a library settings file.
   + You can use the file ```./settings/libs/libs_example.json``` as a reference. You can simply copy it and rename it. All files matching the pattern ```libs_NAME.json``` will be read, except ```libs_example.json```.
   + Processor must be selected according to the downloader and the site.
     + ```nhentai``` for **nhentai.net**
     + ```gallery-dl-hitomila``` for **hitomi.la** 
3. Run **app.py**, the server IP address will appear in the terminal.

### Chrome-Extension
There is an extension for chromium-based browsers in the ```./extension directory```.
It can be installed via the browser extensions menu **by enabling the developer menu**. The extension simply downloads the open project to the library specified in ```./settings/download/download_targets.json``` (which must exist in ```./sittings/libs```).

*Now only supported for **nhentai.com** via the nhentai downloader, **hitomi.la** will be coming soon.*

*You can specify additional downloader parameters by creating a ```config_nhentai.json``` file in the ```./settings/download directory```, an example file is there under the name ```config_nhentai.example.json```.*