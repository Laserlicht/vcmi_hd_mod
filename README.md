# Heroes of Might & Magic III - HD Edition Mod Creator for VCMI

This repository provides a set of tools to extract assets from the [*Heroes of Might & Magic III - HD Edition*](https://store.steampowered.com/app/297000/Heroes_of_Might__Magic_III__HD_Edition/) and convert them into a mod format compatible with [VCMI](https://vcmi.eu/).

## Features

- **Asset Extraction**: Extracts sprites, bitmaps, and localization files from the HD Edition's `.pak` files.
- **Mod Creation**: Builds mod configurations and generates compatible mod files for VCMI.

## How to Use

### A. Compiled Release

1. Download `VCMI-HD-Converter-win-AMD64.zip` and extract it.
2. Run `VCMI-HD-Converter.exe`. Ensure you have at least **10GB free space** to successfully create the mod for VCMI.
3. Follow the prompts:
   - Select the installation folder of *Heroes of Might & Magic III - HD Edition*.
   - Choose the output folder for the generated mod.
4. After the process completes:
   - Copy the generated mod files to the `Mods` directory of your VCMI installation.

### B. Python Script

1. **Clone this Repository**

   ```bash
   git clone https://github.com/yourusername/homm3-hd-mod-vcmi.git
   cd homm3-hd-mod-vcmi
   ```

2. **Install Requirements**

   Ensure the following Python dependencies are installed:

   ```plaintext
   numpy==1.26.4
   pillow==10.2.0
   pandas==2.1.4
   SciPy==1.11.4
   ```

   Install them using:

   ```bash
   pip install -r requirements.txt
   ```


3. **Run the Script**

   ```bash
   python main.py
   ```

4. **Follow the Prompts**

   - Select the installation folder of *Heroes of Might & Magic III - HD Edition*.
   - Choose the output folder for the generated mod.

5. After the process completes:
   - Copy the generated mod files to the `Mods` directory of your VCMI installation.
