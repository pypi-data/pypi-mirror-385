from setuptools import setup, find_packages;setup(name='anemone_daisy_maker',version='1.96',entry_points={'console_scripts':['anemone=anemone.__init__:anemone']},license='Apache 2',platforms='any',url='http://ssb22.user.srcf.net/indexer/anemone.html',author='Silas S. Brown',author_email='ssb22@cam.ac.uk',description='Create DAISY digital talking books from HTML text, MP3 audio and JSON time index data',long_description='''Anemone DAISY maker
-----------------
from http://ssb22.user.srcf.net/indexer/anemone.html

anemone is a module to put together a DAISY digital talking book, from HTML text, MP3 audio recordings and time index data.  It produces DAISY 2.02 files by default, or DAISY 3 (i.e. ANSI/NISO Z39.86) if an option is set.  It can produce four different types of digital talking book:

1. Full audio with basic Navigation Control Centre only: this requires a list of MP3 or WAV files for the audio, one per section, and the title of each section can be placed either in a separate text file or in the filename of the audio file.

2. Full audio with full text: this requires MP3 or WAV files for the audio, corresponding XHTML files for the text, and corresponding JSON files for the timing synchronisation.  Each JSON file is expected to contain a list called `"markers"` whose items contain `"id"` (or `"paragraphId"` or anything else ending `id`) and `"time"` (or `"startTime"` or anything else ending `time`), which can be in seconds, minutes:seconds or hours:minutes:seconds (fractions of a second are allowed in each case).  The IDs in these JSON files should have corresponding attributes in the XHTML, by default `data-pid` but this can be changed with an option.

3. Text with no audio: this requires just XHTML files, and extracts all text with a specified attribute (`data-pid` by default)

4. Text with some audio: this is a combination of the above two methods, and you’ll need to specify `skip` in the JSON file list for the chapters that do not yet have recorded audio

All files are placed on the command line (or in parameters if you’re using Anemone as a module), and Anemone assumes the correspondences are ordered.  So for example if MP3, HTML and JSON files are given, Anemone assumes the first-listed MP3 file corresponds with the first-listed HTML file and the first-listed JSON file, and so on for the second, third, etc.  With most sensible file naming schemes, you should be able to use shell wildcards like `*` when passing the files to Anemone.  You may also set the name of an output file ending `zip`; the suffix `_daisy.zip` is common.  The title, publisher, language etc of the book should be set via options: run the program with `--help` to see all.

The daisy anemone is a sea creature on the rocky Western shores of Britain and Ireland; the Dorset Wildlife Trust says it’s “usually found in deep pools or hiding in holes or crevices, or buried in the sediment with only tentacles displayed”.  Similarly this script has no interactive user interface; it hides away on the command line, or as a library module for your Python program.

### Behaviour of DAISY readers in 2024

* Dolphin EasyReader 10 (iOS, Android and Chromebook): is able to open the ZIP and play the audio while highlighting the paragraphs in a ‘full audio plus full text’ book, both Daisy 2 and Daisy 3.  In very large books (over 1&nbsp;GB), loading and navigation becomes unreliable.  An Internet connection is required the first time a book is opened.

* EDRLab Thorium Reader (Windows, Mac and GNU/Linux): is able to open the ZIP and play the audio while highlighting the paragraphs in a ‘full audio plus full text’ book, both Daisy 2 and Daisy 3.  Still works in very large books but loading is slow.  Version 2.4 might be more responsive than version 3.0.

* Dolphin EasyReader 10 (Windows): is able to play audio while highlighting paragraphs in both Daisy 2 and Daisy 3, but ZIP needs to be unpacked separately and NCC or OPF file opened.  Very large (1 GB+) books can cause the program to crash when Search is used.

* JAWS FSReader 3 (Windows): is able to play audio while highlighting paragraphs in both Daisy 2 and Daisy 3, but ZIP needs to be unpacked separately and NCC or OPF file opened; may work better without JAWS running; synchronisation with audio seems to require `mp3_recode`; images are not scaled to fit; tested working with a Braille display and audio speed changes; not tested with very large books (1GB+)

* HumanWare Brailliant: does not show text if there is audio (hopefully it can still be used for navigation); ZIP needs to be unpacked; tested both Daisy 2 and Daisy 3 (which the device calls "Niso" format)

does not show text if there is audio (hopefully it can still be used for navigation) in both Daisy 2 and Daisy 3

* Pronto Notetaker: ZIP needs to be unpacked to a “Daisy” folder on SD or USB, and the device just plays the audio; tested only with Daisy 2

* US Library of Congress NLS Player: unpack the ZIP onto a blank USB stick of capacity 4 GB or less—plays; navigation works if you use `mp3_recode`; tested only with Daisy 2 but the documentation says Daisy 3 should work

* HumanWare Victor Reader Stream: ZIP needs to be unpacked, either to the top level of a USB device, or into a subfolder of a `$VRDTB` folder on the SD card (different books will be listed alphabetically).  If it’s unpacked at the top level of the SD card, the device can still play the MP3s and allow track or time based navigation but not section navigation, so you should use either the folder structure of the SD card or else a USB device.  If correctly set up then audio plays and device can navigate by section.  Tested with both Daisy 2 and Daisy 3.

* HumanWare Victor Reader Stratus4: When unpacking the ZIP to CD, please ensure that your CD writer does *not* create a *folder* with the same name as the ZIP: this default behaviour of Microsoft Windows does *not* result in a valid Daisy CD.  The individual *files* of the ZIP need to be written to the *top level* of the CD, *not* to a folder on it.  Otherwise, the Stratus4 will not recognise the CD as a Daisy CD and will just play the MP3s, resulting in only time and track based navigation being available.  Tested with both Daisy 2 and Daisy 3.

* HIMS QBraille XL: can display the text (after opening with Space and Enter); does not play audio; ZIP needs to be unpacked; tested only with Daisy 2

* Daisy Consortium Simply Reading 3 (app available for Android 7 and below): is able to open the ZIP and play the audio while highlighting the paragraphs in a ‘full audio plus full text’ book, although fonts for some languages might be missing on earlier Android devices

* DAISY Pipeline (2023): Please do not use this to convert an Anemone-produced Daisy 2 book to Daisy 3.  The resulting Daisy 3 is not likely to play on anything.  If Daisy 3 is required, use Anemone’s `daisy3` option to produce it directly.

Copyright and Trademarks
----------------------

© Silas S. Brown, licensed under Apache 2.

* Android is a trademark of Google LLC.

* Apache is a registered trademark of The Apache Software Foundation.

* Linux is the registered trademark of Linus Torvalds in the U.S. and other countries.

* Mac is a trademark of Apple Inc.

* Microsoft is a registered trademark of Microsoft Corp.

* MP3 is a trademark that was registered in Europe to Hypermedia GmbH Webcasting but I was unable to confirm its current holder.

* Python is a trademark of the Python Software Foundation.

* Windows is a registered trademark of Microsoft Corp.

* Any other trademarks I mentioned without realising are trademarks of their respective holders.''',long_description_content_type='text/markdown',packages=find_packages(),classifiers=['Programming Language :: Python :: 3','License :: OSI Approved :: Apache Software License','Operating System :: OS Independent'],python_requires='>=3.7',install_requires=['mutagen','beautifulsoup4'])
