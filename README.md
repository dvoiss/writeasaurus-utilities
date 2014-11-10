These scripts retrieve the prompts from Reddit, edit them, and prepare them to be put into a sqlite3 DB that would go into the [Writeasaurus](http://writeasaurus.com) app.

Enter reddit credentials and it downloads all the prompts:

	$ python writeasaurus_fetch.py -h
	writeasaurus_fetch.py -u <username> -p <password>

Run the release script and it packages them into a SQLite DB, if the filter flag is passed the script asks you to approve each prompt one by one and edit them. This was important since the app was put into the education section and some of the prompts wouldn't have met Google's content guidelines for Android.

	$ python writeasaurus_release.py -h
	writeasaurus_release.py -f

Install, use [pip](https://pip.readthedocs.org/en/latest/installing.html):

	$ pip install -r requirements.txt

The library file is used by the other two, but when run as a script it has a main entry point that runs through a simple test harness:

	$ python writeasaurus_library.py
	starting test...
	creating database helper
	opening connection to database
	clearing database
	creating database
	create mock data
	select recently inserted data:
	[(1, u'A test description', u'Source ID (Reddit ID)', u'extra-text', 1415639306), (2, u'Another description', u'Source ID (Different Source ID)', u'extra-text-2', 1415639306)]

	resetting database
	finishing test...

<a href="http://play.google.com/store/apps/details?id=com.github.dvoiss.writeasaurus" rel="Writeasaurus Play Store Link">![Writeasaurus Play Store Link](https://developer.android.com/images/brand/en_app_rgb_wo_60.png)</a>
