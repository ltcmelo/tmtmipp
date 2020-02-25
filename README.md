# TMTMIPP

The Most Trivial Markup Include Pre-Processor

Think of this as an automated copy & paste of HTML chunks so that you can reuse content when building a website.
For a better contextual description, take a look at this article: [The Simplest Ways to Handle HTML Includes](https://css-tricks.com/the-simplest-ways-to-handle-html-includes/).

TMTMIPP works through pre-processing: it outpus a version of the input where
tags

`<!--@#$ path/to/relative/file.html -->` 

are replaced by the text of the referenced file.

## Example

```
git clone git@github.com:ltcmelo/tmtmipp.git
cd tmtmipp
./pp.py example
```

By default, a directory named `output` will be created; inside it, you should find a ready-to-be-deployed website.
