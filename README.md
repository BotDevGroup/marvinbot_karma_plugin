# Marvinbot Karma Plugin

A plugin that count the likes or dislikes from the group and show reports of likes and dislikes.

# Requirements

-   A working [Marvinbot](https://github.com/BotDevGroup/marvin) install

# Getting Started

Download the source:

```
$ git clone git@github.com:BotDevGroup/marvinbot_karma_plugin.git
```

Install the plugin into your virtualenv:

```
(venv)$ python setup.py develop
```

Open your marvinbot `settings.json` and `marvinbot_karma_plugin` to your `plugins` list.

## Rationale:
This plugin uses a Statistical algorithm to keep track of some states. The
algorithm in question is Hyperloglog, it has an accuracy of 99% and a very
low memory footprint (5kb maybe?), perfectly acceptable for our use case.

Please refer to the following link for more information about Hyperloglog:
- http://basho.com/posts/technical/what-in-the-hell-is-hyperloglog/
- https://en.wikipedia.org/wiki/HyperLogLog
