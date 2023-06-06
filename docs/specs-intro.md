# Introduction

The following are the specifictions for nydok itself, to serve as an example of how the specifications not only can be turned into a CSV report, but can also easily be included alongside the documentation of the software itself.


## Markdown plugin

nydok includes a [Python-Markdown](https://python-markdown.github.io/) plugin that can be applied when rendering the specifications in the documentation into HTML.

It will render the requirements as a HTML table with nydok-specific classes, letting you style them as you wish. You can see examples of this in this documentation.

```html
<table class="nydok-requirements">
    <tr>
        <td class="req-id">FR001</td>
        <td class="req-refs"></td>
        <td class="req-desc">Requirement description</td>
    </tr>
    <tr>
        <td class="req-id">FR002</td>
        <td class="req-refs">UR002</td>
        <td class="req-desc">Requirement description</td>
    </tr>
</table>
```

### Usage

!!! note
    The plugin only works with the default regex pattern for requirements.

How the use the plugin will vary depending on how you render your documentation. The following are two examples of how to use it in Python and with [MkDocs](https://www.mkdocs.org/).


#### Python

```python

import markdown
from nydok.markdown_ext import nydok as NydokExtension

html = markdown.markdown(
    markdown_text,
    extensions=[
        NydokExtension()
    ]
)
```

#### MkDocs

```yaml
# mkdocs.yml

markdown_extensions:
    - nydok.markdown_ext:nydok
```

