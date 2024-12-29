# SV.ViewerH

___
*Save your collection*

![](./docs/screenshot_main_1.png)

### Features:

- View projects from **nhentai.net** downloaded using [nhentai][1].
- View projects from **hitomi.la**, **nhentai.net** (and other **sites** in the future) downloaded
  using [gallery-dl][2].
- Browser extension that allows you to easily download an open project page from supported sites.
- Shows already uploaded projects directly on the website (hitomi.la)

### SV.ViewerH is a viewer for images uploaded via:

- [nhentai][1]
- [gallery-dl][2]

### Supports

| Site        | Supported downloader           | Extension (download)                      | Extension (extra)                      |
|-------------|--------------------------------|-------------------------------------------|----------------------------------------|
| nhentai.net | [nhentai][1] / [gallery-dl][2] | supported([nhentai][1] / [gallery-dl][2]) | none                                   |
| hitomi.la   | [gallery-dl][2]                | supported([gallery-dl][2])                | show already downloaded on the website |

### Install and run:

#### Using system python

```bash
git clone https://github.com/annihilation7071/SF.ViewerH.git
cd SV.ViewerH
pip install -r requirements.txt
app.py
```

#### Using venv

```bash
git clone https://github.com/annihilation7071/SF.ViewerH.git
cd SV.ViewerH
python -m venv venv
./venv/scripts/activate
pip install -r requirements.txt
app.py
```

### How to start:

1. Upload files using [nhentai][1] or [gallery-dl][2]. (```--write-info-json``` parameter **MUST** be used
   for [gallery-dl][2])
2. Create a library settings file.
    + You can use the file ```./settings/libs/libs_example.json``` as a reference. You can simply copy it and rename it.
      All files matching the pattern ```libs_NAME.json``` will be read, except ```libs_example.json```.
    + Processor must be selected according to the downloader and the site.
        + ```nhentai``` or ```gallery-dl-nhentai``` for **nhentai.net**
        + ```gallery-dl-hitomila``` for **hitomi.la**
3. Run **app.py**, the server IP address will appear in the terminal.

### Chrome-Extension

There is an extension for chromium-based browsers in the ```./extension directory```.
It can be installed via the browser extensions menu (*just **drag** the .crx into the extensions tab and
click **install***). The extension simply downloads the open project to the library specified in
```./settings/download/download_targets.json``` (which must exist in ```./sittings/libs```).

*You can specify some additional downloader parameters by creating
a ```config_nhentai.json```/```config_gallery-dl.json``` file in the ```./settings/download directory```, an example
file is there under the name ```config_nhentai_example.json```/```config_gallery-dl_example.json```.*
---
There are two versions of the extension: **Lite** and **Extended**.

**Lite** does nothing except that when you click on the extension icon, it sends the application a link to the currently open page, after which the application tries to download the project from this page.

**Extended** also provides additional functions. At the moment, only one is implemented, this is the display of already downloaded projects on the hitomi.la website.

<img src="./docs/screenshot_extension_1.png" alt="image" width=800>

### Other

---

- Added a function to merge several projects into one.

For example, if you have one of the same project in several languages or in different quality, and you do not want to delete any of them.
<br>All you need to do is on the project page in the options specify the data of similar projects in this format.
<br>`LID:DESCRIPTION:p`<br>
Where **LID** is the **LID** from the project page, **DESCRIPTION** is any description, and **p** is the project that will be the main one. The rest of the projects must be in this format.
<br>`LID:DESCRIPTION`<br>
A new project will be created (virtual, without physical location), which is the main project with the combined tags from all projects. It will also be possible to switch between all projects.
<br><img src="./docs/screenshot_editor_1.png" width=500>

[1]: https://github.com/RicterZ/nhentai

[2]: https://github.com/mikf/gallery-dl
