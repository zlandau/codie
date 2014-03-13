# Codie McHelpsalot

Codie McHelpsalot is a service that:

- Runs on your development machine
- Regenerates ctags files on demand
- Provides fast symbol searching
- Provides full text searching of source code

The primary goal is to do the above in a way that is efficient for large
sourcecode bases. We do this by:

- Using [watchman](https://github.com/facebook/watchman) to update our
  information as files change
- Running as a service, so we don't have to startup every time someone wants to
  lookup a symbol
- Using something like [whoosh](http://pythonhosted.org/Whoosh) to keep a
  full-text index of our source code
- Using bullet points, to fully explain our features

Likely we will support a few modes of operation. I think we need another bullet
list!

- vi/Emacs/whatever ctags support. We want to generate a ctags file so we can
  still use the existing mechanisms
- Editor plugins. We want to be able to do faster symbol searches (for
  autocompletion etc) by having plugins that can query the service
- Command line. We also want to be able to look up symbols and do full text
  searches from the command line.
