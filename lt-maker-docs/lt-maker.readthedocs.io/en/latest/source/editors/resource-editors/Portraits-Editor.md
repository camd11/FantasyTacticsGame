<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

<a href="../../../index.html" class="icon icon-home">lt-maker</a>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" spy="affix" role="navigation"
aria-label="Navigation menu">

<span class="caption-text">Contents:</span>

- <a href="../../home.html" class="reference internal">Lex Talionis
  Wiki</a>

<span class="caption-text">Getting Started:</span>

- <a href="../../getting_started/index.html"
  class="reference internal">Getting Started</a>

<span class="caption-text">Editor Guides:</span>

- <a href="../Editors-Overview.html" class="reference internal">Editors
  Overview</a>
- <a href="../index.html" class="reference internal">Editors</a>
  - <a href="../Editors-Overview.html" class="reference internal">Editors
    Overview</a>
  - <a href="../Level-Editor.html" class="reference internal">Level
    Editor</a>
  - <a href="../Overworld-Editor.html" class="reference internal">Overworld
    Editor</a>
  - <a href="../Event-Editor.html" class="reference internal">Event
    Editor</a>
  - <a href="../database-editors/index.html"
    class="reference internal">Database Editors</a>
  - <a href="index.html" class="reference internal">Resource Editors</a>
    - <a href="Icons-Editor.html" class="reference internal">Icons Editor</a>
    - <a href="Portraits-Editor.html#"
      class="current reference internal">Portraits Editor</a>
      - <a href="Portraits-Editor.html#adding-new-portraits"
        class="reference internal">Adding New Portraits</a>
      - <a href="Portraits-Editor.html#adding-a-new-portrait"
        class="reference internal">Adding a New Portrait</a>
      - <a href="Portraits-Editor.html#modifying-existing-portraits"
        class="reference internal">Modifying Existing Portraits</a>
      - <a href="Portraits-Editor.html#editor-features"
        class="reference internal">Editor Features</a>
      - <a href="Portraits-Editor.html#misc" class="reference internal">Misc</a>
    - <a href="Map-Animations-Editor.html" class="reference internal">Map
      Animations Editor</a>
    - <a href="Backgrounds-Editor.html" class="reference internal">Backgrounds
      Editor</a>
    - <a href="Map-Sprites-Editor.html" class="reference internal">Map Sprites
      Editor</a>
    - <a href="Combat-Animations-Editor.html"
      class="reference internal">Combat Animations Editor</a>
    - <a href="Tilemaps-Editor.html" class="reference internal">Tilemaps
      Editor</a>
    - <a href="Sounds-Editor.html" class="reference internal">Sounds
      Editor</a>

<span class="caption-text">Events:</span>

- <a href="../../events/index.html" class="reference internal">Events</a>

<span class="caption-text">Guides:</span>

- <a href="../../guides/Guides-Overview.html"
  class="reference internal">Guides Overview</a>
- <a href="../../guides/index.html" class="reference internal">Guides</a>

<span class="caption-text">appendix:</span>

- <a href="../../appendix/Text-Formatting-Commands.html"
  class="reference internal">Text Formatting Commands</a>
- <a href="../../appendix/Item-Component-Reference.html"
  class="reference internal">Item Component Dictionary</a>
- <a href="../../appendix/Skill-Component-Reference.html"
  class="reference internal">Skill Component Dictionary</a>
- <a href="../../appendix/Special-Variables.html"
  class="reference internal">Special Variables</a>
- <a href="../../appendix/Special-Tags.html"
  class="reference internal">Special Tags</a>
- <a href="../../appendix/trigger-reference.html"
  class="reference internal">Event Triggers</a>
- <a href="../../appendix/Random-Seed-Mechanics.html"
  class="reference internal">Random Seed Mechanics</a>
- <a href="../../appendix/FAQ.html" class="reference internal">Frequently
  Asked Questions</a>
- <a href="../../appendix/Contributing_to_the_LTWiki.html"
  class="reference internal">Contributing to the LTWiki</a>
- <a href="../../appendix/index.html" class="reference internal">Code
  Documentation</a>

</div>

</div>

<div class="section wy-nav-content-wrap" toggle="wy-nav-shift">

[lt-maker](../../../index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="Page navigation">

- <a href="../../../index.html" class="icon icon-home"
  aria-label="Home"></a>
- [Editors](../index.html)
- [Resource Editors](index.html)
- Portraits Editor
- <a
  href="https://gitlab.com/rainlash/lt-maker/blob/master/docs/source/editors/resource-editors/Portraits-Editor.md"
  class="fa fa-gitlab">Edit on GitLab</a>

------------------------------------------------------------------------

</div>

<div class="document" role="main" itemscope="itemscope"
itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="portraits-editor" class="section">

# Portraits Editor<a href="Portraits-Editor.html#portraits-editor" class="headerlink"
title="Link to this heading"></a>

*last updated 2025-04-20*

The Portraits Editor lets you add or modify portraits that can be used
for characters in the engine.

![Editor](./media/be508c2ac4efec091637464a477ef19108373cab.png)

<div id="adding-new-portraits" class="section">

## Adding New Portraits<a href="Portraits-Editor.html#adding-new-portraits" class="headerlink"
title="Link to this heading"></a>

Portraits are imported as PNGs in a single sprite sheet. The **Raw
Sprite** preview section on the bottom right of the Portrait Editor
shows the format that the editor expects a portrait to be in. There are
a few components to the portrait format.

![Eirka Sprite
Sheet](./media/57e98eb886fcee2d841ff8f2ae7dc98238dc7927.png)

**Dimensions**: The editor expects sprite sheets to be 128x112 pixels.

**Background Color**: The editor wants the background color to be the
<span class="pre">`#80a080`</span> hex code shade of green. This is a
very specific color that the engine is set to ignore, allowing for a
transparent background in game. The editor will try to force the
background color of your imported sprite sheet to be green.

**Sections**: The image below specifies the sections expected in the
sprite sheet. There is some extra unused space at the top and bottom
right that is in the shade <span class="pre">`#80a080`</span>. There are
11 sections in the portrait sprite sheet, these are separated more
generally into: face, minimug, eyes, and mouth sections. The mouth
sections are split into smile frame A-C, neutral frame A-C and status
screen frame. The eye sections are split into blinking frame A-B. These
frames are overlaid onto the face to create talking and blinking
animations.

![Sprite Sheet
Format](./media/684e41763f05c9052e558a566fc074f66dd06b57.png)

Make sure your portraits are in this specific format before you add it
to the editor. Feel free to download the above image to use as a
template for creating sprite sheets.

</div>

<div id="adding-a-new-portrait" class="section">

## Adding a New Portrait<a href="Portraits-Editor.html#adding-a-new-portrait" class="headerlink"
title="Link to this heading"></a>

You can add new portraits by clicking the
<span class="pre">`Add`</span>` `<span class="pre">`New`</span>` `<span class="pre">`Unit`</span>` `<span class="pre">`Portrait...`</span>
button. This will bring up a window for you to navigate to your PNG
sprite sheet to import it into the editor.

After importing, the editor will run two automatic steps. If the
portrait sprite sheet is given in the correct format as described above,
the editor will automatically try to place the mouth and eye frames on
the face based on image similarity. If the editor fails to find a
matching location the mouth and eye frames will be placed in the top
left. The editor will also automatically recolor the background of the
portrait sprite sheet to be <span class="pre">`#80a080`</span> based on
the background color of the face section.

The editor *will not* initially make a copy of the file you import. This
means that the automatic colorkey algorithm may modify the colors in the
file you import. If that is something you care about make a copy of the
portrait sprite and import the copy instead. Once you save your project
the editor will create a copy of the portrait inside of your project.

</div>

<div id="modifying-existing-portraits" class="section">

## Modifying Existing Portraits<a href="Portraits-Editor.html#modifying-existing-portraits"
class="headerlink" title="Link to this heading"></a>

Editing existing portraits is as easy as opening the PNG file associated
with each portrait imported into the editor in the image manipulation
software of your choice and editing it. The already imported portraits
can be found under
<span class="pre">`your_project.ltproj/resources/portraits/`</span>. You
can then click on the portrait in the editor and edit the extra
settings.

</div>

<div id="editor-features" class="section">

## Editor Features<a href="Portraits-Editor.html#editor-features" class="headerlink"
title="Link to this heading"></a>

The editor has a few extra features that are available for use after
importing the portrait sprite sheet. To show what they do this guide
will import the above portrait format image into the editor as a
demonstration.

You will notice that after importing the portrait sprite sheet into the
editor the background on the face section has automatically been changed
to <span class="pre">`#80a080`</span>. This is a feature of the editor
to make importing sprite sheets from other engines that expect a
different color background to be a slightly smoother process. If this
feature of the editor created any problems for you refer to the
<a href="Portraits-Editor.html#modifying-existing-portraits"
class="reference internal">Modifying Existing Portraits</a> section. The
editor will also automatically try to place the mouth and eye frames on
the face based on image similarity. If the editor fails to find a
matching location the mouth and eye frames will be placed in the top
left.

![Format Sprite Sheet Imported Into
Editor](./media/7f2492432d00b4f0d808b7ec2708db0f7fad20f7.png)

The
<span class="pre">`Portrait`</span>` `<span class="pre">`Selector`</span>
section of the editor on the left, you can see the minimug section is
previewed as the unit icon.

In the
<span class="pre">`Portrait`</span>` `<span class="pre">`Preview`</span>
section of the editor on the right, you can see that the editor has
overlaid the neutral frame A section of the portrait sprite sheet onto
the face section. The background is also transparent as the background
has been changed to <span class="pre">`#80a080`</span>.

![format sprite sheet in the
editor](./media/46ca2cdf60c030bc8c080fd6fb2fa840c50badc1.png)

Below the preview, you will find three buttons:
<span class="pre">`Smile`</span>, <span class="pre">`Talk`</span>, and
<span class="pre">`Blink`</span>. These three buttons are responsible
for controlling what is displayed in the preview section.
<span class="pre">`Smile`</span> will overlay smile frame A onto the
portrait. <span class="pre">`Talk`</span> will cycle through smile frame
A-C and overlay it onto the portrait. <span class="pre">`Blink`</span>
will quickly overlay blinking frame A before transitioning to blinking
frame B. These three buttons make it easy for you to position the
overlays and check what the portraits will look like in your game.

The status screen section of the portrait sprite sheet will be overlaid
at the same location as the mouth frames and will be used when
displaying the character in the info/status screen in the game.

On the right of the preview there are three settings you can adjust: the
<span class="pre">`Blinking`</span>` `<span class="pre">`Offset`</span>,
the
<span class="pre">`Smiling`</span>` `<span class="pre">`Offset`</span>
and the
<span class="pre">`Info`</span>` `<span class="pre">`Menu`</span>` `<span class="pre">`Offset`</span>.
The
<span class="pre">`Blinking`</span>` `<span class="pre">`Offset`</span>
controls where the mouth frames are overlaid over the face. The
<span class="pre">`Blinking`</span>` `<span class="pre">`Offset`</span>
controls where the eye frames are overlaid over the face. The
<span class="pre">`Info`</span>` `<span class="pre">`Menu`</span>` `<span class="pre">`Offset`</span>
controls the vertical offset of the entire portrait displayed in the
info/status screen in game.

An example of this can be seen in the image below, where the blinking
frame has been overlaid on the face by toggling the
<span class="pre">`Blink`</span> button and all of the offsets have been
adjusted to reasonable locations.

![format sprite sheet in the editor after adjusting
offsets](./media/25d0aa30e087778d5d4c9de3dd696f780b31b808.png)

<span class="pre">`Smile`</span> and <span class="pre">`Talk`</span>
will use the same
<span class="pre">`Smiling`</span>` `<span class="pre">`Offset`</span>
as they are both mouth frames, so you will be able to immediately spot
if it is in the wrong position. However,
<span class="pre">`Blinking`</span>` `<span class="pre">`Offset`</span>
used by the eye frames will not be shown by default, so make sure to
toggle the <span class="pre">`Blink`</span> option at least once to
check.

![Normal?](./media/8bd06b594c4d7e80c346ef5c94b43897352e8036.png)
![Oops](./media/f8b0f073491df96df1ec176b9aac802d48c4346e.png)

The
<span class="pre">`Auto-guess`</span>` `<span class="pre">`Offsets`</span>
button runs an algorithm that tries to automatically overlay the mouth
and eye frames at appropriate locations on the face based on an image
similarity algorithm. If the algorithm fails you can manually adjust the
offsets in the
<span class="pre">`Blinking`</span>` `<span class="pre">`Offset`</span>
and
<span class="pre">`Smiling`</span>` `<span class="pre">`Offset`</span>
fields. This step is automatically run for new sprite sheets imported
into the editor. The
<span class="pre">`Automatically`</span>` `<span class="pre">`colorkey`</span>
button runs an algorithm that changes the background color to
<span class="pre">`#80a080`</span> based on the background color of the
face section. This step is also automatically run for new sprite sheets
imported into the editor.

Press <span class="pre">`OK`</span> or <span class="pre">`Apply`</span>
to save any changes.

After adding a new sprite, you can now use it as a unit portrait in the
**Unit Editor**. You can see that the portrait displayed lines up with
the
<span class="pre">`Info`</span>` `<span class="pre">`Menu`</span>` `<span class="pre">`Offset`</span>
selected in the portrait editor.

![portrait used in unit
editor](./media/ed57c2a8962e829312c3ac5f357d690199de724d.png)

</div>

<div id="misc" class="section">

## Misc<a href="Portraits-Editor.html#misc" class="headerlink"
title="Link to this heading"></a>

When referencing a portrait directly in a
<span class="pre">`speak`</span> command, the text log feature will use
the name of the portrait within this editor as the name of the speaker
in the backlog. Remember this to avoid (or subtly place) spoilers in
your text.

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="Footer">

<a href="Icons-Editor.html" class="btn btn-neutral float-left"
accesskey="p" rel="prev" title="Icons Editor"><span
class="fa fa-arrow-circle-left" aria-hidden="true"></span> Previous</a>
<a href="Map-Animations-Editor.html" class="btn btn-neutral float-right"
accesskey="n" rel="next" title="Map Animations Editor">Next <span
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
