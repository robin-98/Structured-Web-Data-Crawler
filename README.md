# Overview

This is an open source, multi-threaded website crawler based on the [Spider](https://github.com/buckyroberts/Spider) project.

It can crawl websites according to a JSON configuration file, in which you can specify detailed components in some webpages using jQuery style selectors. And those components will be stored in appropriate files under the project directory which is also specified in the configuration file.

## Quick Start

`python ./main.py ./example-cfg.json`


## Configuration File Example

Let's take one of the most popular news website in China as example:

```json
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
        "storage": {
          "pages_per_dir": 300,   // every directory store datas from 300 pages
          "format": "json"        // data parsed from each page is organized in dictionary and dumped in json file
        },
        "sub_domains": [
          "news.sina.com.cn"      // Constrain targets on some domains in the crawled webpages
        ],
        "sub_urls": [
          "/c/\\d+-\\d+-\\d+"         // Constrain targets on some sub-path in the crawled webpages, it's always the beginning sub-string of those paths
          // if the string contain '\\', it represent a regex expression
        ],
        "components": [{          // Some area in the webpage
          "role": "photo",        // to identify the component
          "format": "image",      // supported formats: image, text, json, table
                                  // image resource while be downloaded in the same directory as the page content, and in the page content there will be the resource file name, not the original url
          "selector": "#article > div > img"  // jQuery style selector, while not exactly the same
        },{
          "role": "title",
          "format": "text",
          "selector": "body > div.main-content > h1"
        },{
          "role": "article",
          "format": "text",
          "selector": "#article"
        },{
          "role": "comments",
          "format": "table",      // parse structured data embedded in the page while without concrete amount of rows
          "selector": "body > div.comment > table",
          "sub_components": [{
            "role": "user_name",
            "format": "text",
            "sub_selector": "tr > td:nth-child(1)"  // the relevative selector according to its parent selector, you can also use absolute selector but use 'selector' property instead
          },{
            "role": "comment",
            "format": "text",
            "sub_selector": "tr > td:nth-child(3)"
          },{
            "role": "avatar",
            "format": "image",
            "sub_selector": "tr > td:nth-child(2)"
          }]
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

1. Other attributes can also be used, just connect with `:` one by one, such as:
 `input.s-inpt:type=text:name=p:value=priority`
means an `input` tag has at least one class name `s-inpt` and at least have three other attributes `type`, `name`, and `value`, which values should be `text`, `p`, and `priority` respectively


## Storage organization

```shellscript
--<data_dir>
 |--<project_name>
   |--<version>
     |--<target_component set name>
       |--<random hashed directory>
         |--file_to_url.json
         |--url_to_file.json
         |--<random hashed file name according to each url>.json
         |--<component role>_<index of the component>_<random hash>_[_<raw file name>].<txt/jpg/png/json>
```

# Enjoy!

