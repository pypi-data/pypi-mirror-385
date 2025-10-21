
# Mirrorit

This **cli tool** can mirror your subject very clever and easy in different ways.

## Installation

The installation proccess can be done using the pip tool:
```
pip install mirrorit
```

### Project Link
[Project link in Pypi](https://www.pypi.org/project/mirrorit)

[Project link in Github](https://www.github.com/Lunethra/Mirrorit)
## Documentation

A help doc is in the tool but the main documentaion is here:  
(the tool doc is accessed using "mirrorit --help" or "mirrorit -h")  

Mirroring can be done in multiple ways:  
  -
  1.mirroring the **whole** text. (--mode w)  
  2.mirroring the **lines** of the text (--mode l)  
  3.mirroring every word of the text without changing the index of words (--mode t)  
  4.mirroring every word of the text without changing the index of words, split words between symbols and spaces. (--mode k)

Working with files also has multiple ways:
  | Different modes of working with files |
  |---|
  1.Overwriting the file (-s)  
  2.Saving output as a new file (-n)  
  3.Just showing the output in terminal (-j)  

### Difference between mode "t" and mode "k"
in mode "k" the words are splited with the spaces between them.  
### Example of words spliting in "t" and "k" mode
file.txt:
```txt
Lune Lu!ne !Lu!ne! !Lu!ne
```
second command:
```shell
mirrorit file.txt -m t -j
Output:
enuL en!uL !en!uL! !en!uL
```
command:
```shell
mirrorit file.txt -m k -j
Output:
enuL uL!en !uL!en! !uL!en
```


as you can see, the text mirroring is different.

⚠️ You cannot enter more than one word when using the cli (not file) mode.  
This means you cannot enter spaces in input.
## Usage/Examples

You can use the tool by just giving the name you want to greet.
```bash
Mirrorit Lunethra
Output: arhtenuL
```

or say mirror files.
```bash
mirrorit file.txt -s
Output: mirrored_file.txt
```
## Support

To resolve issues and make suggestions, please visit the project's GitHub page.


## License

This project uses [MIT License](https://github.com/Lunethra/Mirrorit/blob/main/LICENSE).

