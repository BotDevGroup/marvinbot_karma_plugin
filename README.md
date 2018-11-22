marvinbot_karma_plugin

## Rationale:
This plugin uses a Statistical algorithm to keep track of some states. The
algorithm in question is Hyperloglog, it has an accuracy of 99% and a very
low memory footprint (5kb maybe?), perfectly acceptable for our use case.

Please refer to the following link for more information aboyt Hyperloglog:
- http://basho.com/posts/technical/what-in-the-hell-is-hyperloglog/
- https://en.wikipedia.org/wiki/HyperLogLog
