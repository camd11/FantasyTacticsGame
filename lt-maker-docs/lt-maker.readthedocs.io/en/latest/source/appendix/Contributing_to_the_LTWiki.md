<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

<a href="../../index.html" class="icon icon-home">lt-maker</a>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" spy="affix" role="navigation"
aria-label="Navigation menu">

<span class="caption-text">Contents:</span>

- <a href="../home.html" class="reference internal">Lex Talionis Wiki</a>

<span class="caption-text">Getting Started:</span>

- <a href="../getting_started/index.html"
  class="reference internal">Getting Started</a>

<span class="caption-text">Editor Guides:</span>

- <a href="../editors/Editors-Overview.html"
  class="reference internal">Editors Overview</a>
- <a href="../editors/index.html" class="reference internal">Editors</a>

<span class="caption-text">Events:</span>

- <a href="../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../guides/Guides-Overview.html"
  class="reference internal">Guides Overview</a>
- <a href="../guides/index.html" class="reference internal">Guides</a>

<span class="caption-text">appendix:</span>

- <a href="Text-Formatting-Commands.html" class="reference internal">Text
  Formatting Commands</a>
- <a href="Item-Component-Reference.html" class="reference internal">Item
  Component Dictionary</a>
- <a href="Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="Special-Variables.html" class="reference internal">Special
  Variables</a>
- <a href="Special-Tags.html" class="reference internal">Special Tags</a>
- <a href="trigger-reference.html" class="reference internal">Event
  Triggers</a>
- <a href="Random-Seed-Mechanics.html" class="reference internal">Random
  Seed Mechanics</a>
- <a href="FAQ.html" class="reference internal">Frequently Asked
  Questions</a>
- <a href="Contributing_to_the_LTWiki.html#"
  class="current reference internal">Contributing to the LTWiki</a>
  - <a href="Contributing_to_the_LTWiki.html#beginner-s-guide"
    class="reference internal">Beginner’s Guide</a>
  - <a href="Contributing_to_the_LTWiki.html#advanced-contributors"
    class="reference internal">Advanced Contributors</a>
    - <a href="Contributing_to_the_LTWiki.html#editing"
      class="reference internal">Editing</a>
    - <a href="Contributing_to_the_LTWiki.html#building-docs"
      class="reference internal">Building Docs</a>
- <a href="index.html" class="reference internal">Code Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../index.html" class="icon icon-home" aria-label="Home"></a>
- Contributing to the LTWiki
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/appendix/Contributing_to_the_LTWiki.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="contributing-to-the-ltwiki" class="section">

# Contributing to the LTWiki<a href="Contributing_to_the_LTWiki.html#contributing-to-the-ltwiki"
class="headerlink" title="Link to this heading"></a>

This page provides information and resources needed to edit the LTWiki.
New contributors and those without Gitlab experience should view the
<a href="Contributing_to_the_LTWiki.html#beginner-s-guide"
class="reference internal">Beginner’s Guide</a> section, while those who
want a cleaner workflow may be interested in the
<a href="Contributing_to_the_LTWiki.html#advanced-contributors"
class="reference internal">Advanced Contributors</a> section.

Regardless, you’ll need a <a href="https://gitlab.com/users/sign_in"
class="reference external">Gitlab Account</a> in order to make edits to
the wiki.

<div id="beginner-s-guide" class="section">

## Beginner’s Guide<a href="Contributing_to_the_LTWiki.html#beginner-s-guide"
class="headerlink" title="Link to this heading"></a>

To begin with, you should be signed into your
<a href="https://gitlab.com/users/sign_in"
class="reference external">Gitlab Account</a>.

Now you can navigate to any page on the
<a href="../../index.html" class="reference external">LT Wiki</a> and
initiate the editor. For this example, let’s alter the
<a href="../getting_started/Getting-Started.html#getting-started"
class="reference internal"><span class="std std-ref">Getting
Started</span></a> page.

![GettingStartedImage](./media/354450de716f0dfc5522e8dde667109079a2a3e6.jpg)

You can click on the
<span class="pre">`Edit`</span>` `<span class="pre">`on`</span>` `<span class="pre">`Gitlab`</span>
link on the top left. This will take you to the repository. You can now
click on the
<span class="pre">`Open`</span>` `<span class="pre">`in`</span>` `<span class="pre">`Web`</span>` `<span class="pre">`IDE`</span>
button:

![GettingStartedImage](./media/7561eb1cbbd855058f983f5cfe8707b1f86f42ae.jpg)

If you haven’t done this before, it will prompt you to
<span class="pre">`Fork`</span> the project. This will create a copy of
the project on your account, which is necessary to make merge requests.
Go ahead and click <span class="pre">`Fork`</span>:

![GettingStartedImage](./media/43e9ff111ae1d6986ed69e6e0b7942f3ceb2490b.jpg)

Wait for the fork to finish. This will take a few seconds. The good news
is, you only need to do this once. Once the initial fork is done, you
will be free to make merge requests directly.

In either case, you should now be able to see the editor. If you want,
you can click on the <span class="pre">`Preview`</span> button to see
how the page is laid out. This helps in understanding the formatting
syntax:

![GettingStartedImage](./media/61baa7c91390eeca65f7fad1dadd82964d862482.jpg)

In either case, you can now make edits freely! Change whatever text you
want (as long as it’s for the good of the wiki). For this tutorial,
let’s make a new article. This one is actually easy to do. Just click
<span class="pre">`New`</span>` `<span class="pre">`File`</span> in the
left pane and it’ll make a new article in the current directory. Use
your best judgement as to where the article goes. I’m going to make an
article in <span class="pre">`Guides`</span> called
<span class="pre">`Contributing`</span>` `<span class="pre">`to`</span>` `<span class="pre">`the`</span>` `<span class="pre">`LTWiki`</span>:

![GettingStartedImage](./media/3165f0001814d418ba54ca3fc8c7506259970372.jpg)

If I add a new file, I also need to add it to the
<span class="pre">`index.rst`</span> file in that directory:

![GettingStartedImage](./media/a1b28ebea32d17e0f66ecf98e764e991007926c2.jpg)

Now that I’ve finished, how do I merge it? This step is quick. Go to the
<span class="pre">`Source`</span>` `<span class="pre">`Control`</span>
icon on the side.

Add a commit message describing your new article.

Finally, click
<span class="pre">`Commit`</span>` `<span class="pre">`and`</span>` `<span class="pre">`Push`</span>.

![GettingStartedImage](./media/841e0067d92c65a8bca1655a70674659a90d22c3.jpg)

Hit <span class="pre">`Enter`</span> through the dialogs - they aren’t
important. You’ll see a dialog pop up telling you that your commit was a
success. Now, you’ll click the
<span class="pre">`Create`</span>` `<span class="pre">`MR`</span>
button, and it’ll take you to the final page:

![GettingStartedImage](./media/1dd141f55f9e581632c45a75fff5947abc26acac.jpg)

![GettingStartedImage](./media/c8a5257153a6c1eddcd674d85d3c3fb801a5399d.jpg)

Where you can fill out some more information on what you changed.
Finally, click the
<span class="pre">`Create`</span>` `<span class="pre">`Merge`</span>` `<span class="pre">`Request`</span>
button.

One of the owners of the repository will approve of your new article,
and after that happens, it’ll be there forever!

</div>

<div id="advanced-contributors" class="section">

## Advanced Contributors<a href="Contributing_to_the_LTWiki.html#advanced-contributors"
class="headerlink" title="Link to this heading"></a>

If you’re already a developer, then you should be generally aware of how
to <a
href="https://docs.gitlab.com/ee/user/project/repository/forking_workflow.html"
class="reference external">fork projects</a>, how to clone projects, and
make upstream merge requests from your own repository.

The LT documentation is kept within the repository, in the
<span class="pre">`docs/`</span> folder. The following commands assumes
that the cwd is inside <span class="pre">`docs/`</span>.

<div id="editing" class="section">

### Editing<a href="Contributing_to_the_LTWiki.html#editing" class="headerlink"
title="Link to this heading"></a>

The documentation source can be found in
<span class="pre">`source/`</span>.

</div>

<div id="building-docs" class="section">

### Building Docs<a href="Contributing_to_the_LTWiki.html#building-docs"
class="headerlink" title="Link to this heading"></a>

Instructions for how to do this can be found in the
<span class="pre">`DEV_README.md`</span> file.

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="FAQ.html" class="btn btn-neutral float-left" accesskey="p"
rel="prev" title="Frequently Asked Questions"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="index.html" class="btn btn-neutral float-right" accesskey="n"
rel="next" title="Code Documentation">Next <span
class="fa fa-arrow-circle-right" aria-hidden="true"></span></a>

</div>

------------------------------------------------------------------------

<div role="contentinfo">

© Copyright 2024, rainlash.

</div>

Built with [Sphinx](https://www.sphinx-doc.org/) using a
[theme](https://github.com/readthedocs/sphinx_rtd_theme) provided by
[Read the Docs](https://readthedocs.org).

</div>

</div>

</div>

</div>
