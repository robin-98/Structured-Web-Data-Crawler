# Overview

This is an open source, multi-threaded website crawler based on the [Spider](https://github.com/buckyroberts/Spider) project.

It can crawl websites according to a JSON configuration file, in which you can specify detailed components in some webpages using jQuery style selectors. And those components will be stored in appropriate files under the project directory which is also specified in the configuration file.

## Quick Start

`python ./main.py ./example-cfg.json`


## Configuration File Example

Let's take one of the most popular news website in China as example:

```javasript
{
  "Structured-Web-Data-Crawler": { // This is the name of the crawler
    "data_dir": "./crawled_sites", // Location to store data files
    "target_sites": [{             // Support multiple sites
      "project_name": "sina",      // Sub-directory name where the data of this website is stored
      "version": "20190228",       // Sub-directory under the <project>
      "threads": 4,                // Threads amount
      "base_url": "https://news.sina.com.cn/china", // Starting point
      "white_list": [
        "news.sina.com.cn"         // Domains to crawl, if left empty, every thing from the start point will be crawled
      ],
      "target_components": [{     // Support multiple settings
        "name": "news",           // Sub-directory under the <project/version>
        "sub_domains": [
          "news.sina.com.cn"      // Constrain targets on some domains in the crawled webpages
        ],
        "sub_urls": [
          "/c/2019-02-28"         // Constrain targets on some sub-path in the crawled webpages, it's always the beginning sub-string of those paths
        ],
        "components": [{          // Some area in the webpage
          "role": "photo",        // to identify the component
          "format": "image",      // supported formats: image, text, json
          "selector": "#article > div > img"  // jQuery style selector, while not exactly the same
        },{
          "role": "title",
          "format": "text",
          "selector": "body > div.main-content > h1"
        },{
          "role": "article",
          "format": "text",
          "selector": "#article"
        }]
      }]
    }]
  }
}
```

## Selector

The `selector` items can be copied from the Chrome Developer Tools (`Mouse right click on some Html tag` -> `Copy` -> `Copy selector`)

***
  
  Notice: selector in this project is not exactly the same as it is in the Chrome Developer Tools

***


The selector is composed with multiple items which are connect with ` > `. *Be careful of the connector, which should be exactly one space plus the character `>` plus one space.* Each item denotes an element in the HTML document tree, and the sequence denotes their hierarchical relationship.

### Selector item format

1. **`id`** has the highest priority: If the element or some of its parent container has property `id`, then the selector can only be or start with `#<the id property>`

1. **`class`** has the second highest priority: every class name is connected by "`.`" after the `tag name`, such as `div.content.title` means a `div` tag have at least two class names: `content` and `title`

1. Other attributes can also be used, just connect with `:` one by one, such as `input.s-inpt:type=text:name=p:value=priority` means an `input` tag has at least one class name `s-inpt` and at least have three other attributes `type`, `name`, and `value`, which values should be `text`, `p`, and `priority` respectively


## Storage organization

```shellscript
--<data_dir>
 |--<project_name>
   |--<version>
     |--<target_component set name>
       |--<hash value of webpage url>
         |--meta.txt    # store the url of the webpage
         |--<component role>_<index of the component>[_<raw file name>].<txt/jpg/png/json>
```

# Enjoy!

