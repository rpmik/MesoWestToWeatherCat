# MesoWest (via Synoptic bulk download) CSV to WeatherCat

LWC format from [https://www.merewether.com/blog/import-wview-data-into-lightsoft-weather-center/242703](https://www.merewether.com/blog/import-wview-data-into-lightsoft-weather-center/242703)

And of course later I found out that WeatherCat has basically the same format but with more tags.

It is important to clean up your CSV data from MesoWest and/or Synoptic.

1. Use the macOS app Numbers to open the CSV. 
1. get rid of rows that have blank key attributes in fields such as air_temp_set_1 and precip_accum_*. 
1. Then delete the metadata at the top, but retain the first header row and delete the second row of units
1. Then by Date_Time column, sort ascending so that time progress forwards toward the end of the file.
1. After that, export the data back out to CSV for processing.
1. Then create folders for each year there's data for. Folders are named YYYY (2018, 2019 etc).
1. Put this script in their parent folder, edit the script, and at minimum change the variable for the starting year and  the CSV file name.
1. Then review the script’s code to make sure it’ll work for you, then on the command line run the script using python3

When the script is done, use bbedit multi-file find and replace the odd upside-down question 
mark character (\x{0D}) in all the files with nothing. No idea why that happens.

**Make a WeatherCat backup!**

**REVIEW THE DATA OUTPUT AND MAKE SURE IT MAKES SENSE BEFORE COPYING TO WEATHERCAT DATA FOLDER!**

**QAQC IS IMPORTANT**

Quit WeatherCat. Being sure you don't overwrite existing data, copy year folders to (usually):

    ~/Library/WeatherCatData/Location1

You may need to append or prefix data in existing WeatherCat data files. If you do that, delete the related .hrs files.

Run WeatherCat and, again, **QAQC the results**. You can restore from backup if needed and adjust the scripts and/or CSV to correct errors.

If you have to rerun the script to tweak things, delete all the previous file outputs! 
Else data will append. This script does no clean-up.
