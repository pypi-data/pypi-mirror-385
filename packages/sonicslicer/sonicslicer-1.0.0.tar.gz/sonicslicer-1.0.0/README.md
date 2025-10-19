# SonicSlicer 🎵✂️

A powerful, well-optimized Python toolkit for splitting and trimming audio files with precision and ease.

---
## Features

- **Smart Audio Splitting**: Split audio files by time duration or file size
- **Precision Trimming**: Trim audio from start/end or specific time ranges
- **Multi-format Support**: Works with WAV, MP3, OGG, FLAC, and AIFF formats
- **Optimized Processing**: Efficient memory usage and fast processing
- **Flexible Output**: Customizable output format and bitrate settings
- **Automatic Naming**: Sequential output filenames with proper numbering

---
## Installation

1. **Install dependencies**:
   ```bash
   pip install pydub
   ```

2. **Install SonicSlicer**:
   ```bash
   pip install sonicslicer
   ```

   Or clone the repository:
   ```bash
   git clone https://github.com/skye-cyber/SonicSlicer.git
   cd sonicslicer
   ```

---
## Usage Examples

#### Splitting Audio Files

**By Size:**

- Split into 1mb chunks
```shell
slicer file.mp3 --split --size 1mb
```
- Split into 100kb chunks, discard small last chunk
```shell
slicer file.mp3 --split --size 100kb --strict -O splits
```

- Single split 5 minutes chunks
```shell
slicer file.mp3 --split --duration 1min
```

**By File Time:**
- Single split 5 minutes chunks
```shell
slicer file.mp3 --split --duration 5min --format ogg
```
- Split into 10 seconds chunks, keep smaller last chunk
```shell
slicer file.mp3 --split --duration 10sec --strict -O splits
```
---
#### Trimming Audio Files

- Trims from 0 to end
```shell
slicer file.mp3 --trim
```

- Discards the first 10 seconds
```shell
slicer fime.mp3 --trim --trim_start 10sec
```

- Discards the last 1 minutes
```shell
slicer fime.mp3 --trim --trim_end 1min
```

- Discards the first 10 and last seconds respectively
```shell
slicer fime.mp3 --trim --trim_start 10sec --trim_end 30sec
```

---
#### Constructor
```python
SonicSlicer(output_format="wav", bitrate="192k")
```
- `output_format`: Output audio format (wav, mp3, ogg, flac, aiff)
- `bitrate`: Bitrate for compressed formats

---
## Performance Tips

1. **Use WAV for processing**: Process in WAV format then convert to compressed formats
2. **Batch processing**: Process multiple files in sequence
3. **Memory management**: For very large files, consider smaller chunk sizes
4. **Output directory**: Use SSDs for faster write speeds when processing large files

---
## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
  See the LICENSE file for more details. See the [LICENSE](LICENSE) file for details.
---
## Support

If you have any questions or issues:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/skye-cyber/SonicSlicer/issues)
3. Create a new issue with detailed information

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

---

**SonicSlicer** - Making audio processing as easy as slicing pie! 🥧
