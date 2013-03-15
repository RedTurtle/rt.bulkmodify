.. contents:: **Table of contents**

Read carefully!
===============

Even if this product is giving you an high level Plone user interface, **it's not designed for end users**
or "*normal*" site administrators.
You must be a `Python regular expression`__ expert (probably a Grand Master).

__ http://docs.python.org/2/howto/regex.html

.. Note:: the product is in **alpha** state. Use at your how risk.

Introduction
============

This product will give to your Plone site managers a tool for performing text search using `regular expressions`__
query and optionally performing text substitutions on the main rich text field of your site's contents.

__ http://en.wikipedia.org/wiki/Regular_expression

How to use
==========

This product is designed for performing the same text type of replacement operation on many documents without
going to edit every ones.

By default the product works with all know rich text fields of Plone contents, that are:

* text field from Page content type
* text field from Event content type
* text field from News Item content type
* text field from Collection content type (old-style also)

You can extending the set above providing 3rd party extensions (see below).

Accessing the "*Bulk modify contents*" panel
--------------------------------------------

In your "Site setup" section you will find a new "*Bulk modify contents*" panel.
All operations take places from this page.

Basic search
------------

The upper section of the page is about searching contents.

.. image:: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-01.png/image_large
   :alt: Search form
   :target: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-01.png/

You must select which content types you want to inspect by checking the "**Content types**" section.
Although this selection display all content types, note that only a subset of them usable (for example: the Link
content types is not using any text field right now).

This selection will trigger a catalog search of all types in the selection (so keep this selection at minimum).

The most important field is the "**Search regex**", where you must write a regular expression.
For every content type found, it's text field will be loaded and text inside wil be parsed for searching matches
with the regex.

You can change some regex search configuration option using the "**Regex flags**" set of checkboxes.

Now you can hit the search button below.

Results
-------

Results of the search are displayed in a table at the bottom of the page.

.. image:: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-02.png/image_large
   :alt: Search form
   :target: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-02.png/

The table will contain a preview of the found text and minimal information about the content.
Please note that a single document can be found multiple time in the table as the minimal entity is the text match,
not the document itself.

Replace text
------------

The simpler way of performing text replacement is get filling the "**Default replacement**" text area.

.. image:: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-05.png/image_large
   :alt: Search form
   :target: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-05.png/

The table of results will change, providing a graphical preview of what will be changed applying your
replacement expression.

.. image:: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-03.png/image_large
   :alt: Search form
   :target: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-03.png/

The user must now select all replacement that he really want to apply, the click the "**Modify selected**" button.
Only selected matches are changed.

.. image:: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-04.png/image_large
   :alt: Search form
   :target: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-04.png/

Replacing options
-----------------

When changing text you are (obviously) changing a Plone content, so you have some additional option available:

*Do not update anything (silent change)*
    Useful if you want to fix some contents without updating other metadata from the content itself.
    Only the text field (and the Plone full text index) will be updated.
    
    Site members will never notice this type of changes.
*Update modification time*
    Update also the last modification time of the document.
*Create a new version (if possible)*
    Full modification. If the content type is versionable, a new version will be saved.

Advanced use
============

Advanced server side operations
-------------------------------

Sometimes a simple text regex expression is not enough.
This product is supporting a way of handling really complex text substitution by calling some server side
components.

By default, only one handler is available: "**Convert internal links to resolveuid usage**", that can transform
Plone internal links to content to a form that use the "``resolveuid``" call.
This can be used in Plone sites where the TinyMCE option "*Link using UIDs*" were not enabled by mistake
(something like the feature given by Kupu editor).

.. image:: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-06.png/image_large
   :alt: Search form
   :target: http://blog.redturtle.it/pypi-images/rt.bulkmodify/rt.bulkmodify-0.1-06.png/

Adding new server side special handlers
---------------------------------------

Proving new ``IBulkModifyReplacementHandler`` utility will automatically display new special replacement::

  <utility
       name="handler_name"
       component="your.product.utility.YourTextSpacialReplacement"
       provides="rt.bulkmodify.interfaces.IBulkModifyReplacementHandler"
    />  

Extending handled types
-----------------------

To being able to change a text field of a type not handled, you must provide a proper adapter with a 3rd party
product::

  <adapter
        for="your.product.interfaces.IYourContentTypeInterface"
        provides="..interfaces.IBulkModifyContentChanger"
        factory="your.product.adapter.YourTextContentAdapter"
        />

TODO
====

* Adding a way for using test substitution also as a running script instance
* We need JavaScript testing 
* The product is designed for performing multiple write commit on ZODB, but probably a
  way of performing a single huge write operation can be useful

Credits
=======

Developed with the support of `Regione Emilia Romagna`__;
Regione Emilia Romagna supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

