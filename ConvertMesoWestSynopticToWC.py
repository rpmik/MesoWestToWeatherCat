import csv
from datetime import datetime, timezone
from os.path import exists

#LWC format from https://www.merewether.com/blog/import-wview-data-into-lightsoft-weather-center/242703
#And of course later I found out that WeatherCat has basically the same format but with more tags.

# It is important to clean up your data from Synoptic. 
# Use Numbers 
# --> get rid of rows that have blank key rows such as air_temp_set_1 and precip_accum_*. 
# --> Then delete the metadata at the top, but retain the first header row and delete the 
#     second row of units
# --> Then by Date_Time column, sort ascending. 
# --> After that, export the data back out to CSV for processing.
# --> Then create folders for each year there's data for. Just named YYYY (2018, 2019 etc).
# --> Put this script in their parent folder, change the variable for the starting year and 
# the CSV file name.  Then review the script’s code to make sure it’ll work for you, then
# run the script using python3
#
# When the script is done, use bbedit multi-file find and replace the odd upside-down question 
# mark character \x{0D} in all the files with nothing. No idea why that happens.
#
# If you have to rerun the script to tweak things, delete all the previous file outputs! 
# Else data will append. This script does no clean-up.

# Initialize global variables........ old school habit.

# CHANGE THESE TWO VARIABLES
startYear = "2018" # year the historical weather data starts
filename = 'F2476.2023-08-13-b.csv' # filename of MesoWest/Synoptic CSV file
inUTC = True

# Start Fresh
lineNumber = 1 # need to start WeatherCat data line numbers at 1, though they might not be strictly necessary.
prevHrPrecip = 0.0
curHrPrecip = 0.0
totalYearlyPrecip = 0.0
hourlyPrecip = 0.0

# I'm not object oriented and using functions isn't necessary for a single task script.

# newline='' is required
with open(filename, newline='') as csvfile: 
	synopticReader = csv.DictReader(csvfile)
	for row in synopticReader:
		#Synoptic time format 2018-03-09T21:32:00Z (aka ISO in UTC; if from MesoWest, could be in local time)
		# None in the pressure field means no data or some other error wide spread 
		# measurement error
		if row['sea_level_pressure_set_1d'] != 'None':
			rowDateTime = datetime.fromisoformat(row['Date_Time'])
			
			if inUTC == True:
				rowDateTimeLocal = rowDateTime.astimezone()
			else:
				rowDateTimeLocal = rowDateTime
				

			#LWC/WC Format
			#t and V are not optional, all other fields are.
			#t is the day, hour and minute (2 digits each), e.g., 01230515
			rowDateTimeLocalLWC = "t:"+rowDateTimeLocal.strftime("%d%H%M")

			#print (str(rowDateTimeLocalLWC))
			#T is outside temperature, 
			rowOutsideTemp = "T:" + row['air_temp_set_1'] 
			#D is dew point, 
			rowDewPoint = "D:" + row['dew_point_temperature_set_1d']
			#Pr is barometric pressure, W is wind speed,
			rowPressure = "Pr:" + str(round(float(row['pressure_set_1d']) * 0.01,4))
			
			# often blank if no wind is measured. It's okay.
			if row['wind_speed_set_1'] != '':
				rowWind = "W:" + str(round(float(row['wind_speed_set_1']) * 3.6,6))
			else: 
				rowWind = 'W:0.0'
			# Wd is wind direction, Wc is wind chill, Wg is wind gust, Ph is hourly precipitation, 
			
			# Wind direction is often blank if there’s no wind speed but the rest of the data is fine
			if row['wind_direction_set_1'] != '':
				rowWindDirection = "Wd:" + row['wind_direction_set_1']
			else: 
				rowWindDirection = "Wd:000"
			
			# Gusts can be blank, so deal with it.
			if row['wind_gust_set_1'] != '':
				rowWindGust = "Wg:" + str(round(float(row['wind_gust_set_1']) * 3.6,6))
			else:
				rowWindGust = "Wg:0.0"
			
			#P is the running total of the year’s precipitation in mm
			# Mesowest CSV uses inches, so need to convert to mm
			rowPrecipTotal = "P:" + str(round(float(row['precip_accum_since_local_midnight_set_1'])*0.0393701,4))
			#H is outside humidity
			rowHumidity = "H:" + row['relative_humidity_set_1']
			# S is solar,
			rowSolar = "S:" + row['solar_radiation_set_1']
			
			# U is UV, (NO UV in Synoptic data) :-(
			#C is current conditions (delimited by double quotes),  (MesoWest/Synoptic doesn’t have)
			#V is validation. Always 4.
			rowValidation = "V:4"
			folder = rowDateTimeLocal.strftime("%Y") # Format as 2022 etc
			if folder != startYear:
				# reset everything to zero
				curHrPrecip = 0.0
				prevHrPrecip = 0.0
				hourlyPrecip = 0.0
				totalYearlyPrecip = 0.0
				startYear = folder
				
			file = rowDateTimeLocal.strftime("%m") # Month in format 01, 02, etc
			
			# WeatherCat datafiles don't have a 0 padded pre-fix, so nuke it.
			file = file.lstrip("0")
			fullPath = folder + "/" + file + "_WeatherCatData.cat"
			rowsAll = [fullPath,rowDateTimeLocalLWC, rowOutsideTemp, rowDewPoint, 
						rowPressure, rowWind,
						rowWindDirection, rowWindGust,
						rowHumidity, rowSolar, rowValidation ]
			
			# If the file doesn't exist, create a new file with a fresh header.
			if exists(rowsAll[0]) == False:
				newFile = open (rowsAll[0],'w',newline='')
				# a string "literal"
				header =r"""WeatherCat data file ***If you modify this file, be sure to delete the relevent .hrs file***.
t and V are not optional, all other fields are. 
t is the day, hour and minute (2 digits each), T is outside temperature, Ti is internal temperature,                               T1 to T8 is auxiliary temperatures, D is dew point,                               Pr is barometric pressure, W is wind speed, 
Wd is wind direction, Wc is wind chill, Wg is wind gust, Ph is hourly precipitation, P is total precipitation,
                              H is outside humidity, Hi is internal humidity, H1 to H8 are auxiliary humidity sensors, S is solar, CO21 to CO24 is CO2
Sm1 to Sm4 is soil moisture, Lw1 to Lw4 is leaf wetness, St1 to St4 is soil temperature,
                              Lt1 to Lt4 is leaf temperature, U is UV, Pm is monthly precipitation, Py is annual precipitation, Ed is daily ET, Em is monthly ET, Ey is yearly ET, C is current conditions (delimited by double quotes), V is validation.

VERS:3

"""
# Ph in WeatherCat is the precipitation intensity.
# P is the total precipitation for the year, starting on January 1.
				# Synoptic’s precip_accum_24_hour_set_1 is based on rolling 24hr precipitation and is not useful.
				# Use precip_accum_since_local_midnight_set_1 for accumulation total since midnight
				if row['precip_accum_since_local_midnight_set_1'] != '':
					curHrPrecip = float(row['precip_accum_since_local_midnight_set_1'])
					
				newFile.write(header)
				newFile.close()
				lineNumber = 1
			else:
				
				if curHrPrecip != float(row['precip_accum_since_local_midnight_set_1']):
					
					if float(row['precip_accum_since_local_midnight_set_1']) > 0:
						if float(row['precip_accum_since_local_midnight_set_1']) < curHrPrecip:
							prevHrPrecip = 0.0
						else:
							prevHrPrecip = curHrPrecip
						curHrPrecip = float(row['precip_accum_since_local_midnight_set_1'])
						hourlyPrecip = curHrPrecip - prevHrPrecip
						totalYearlyPrecip += hourlyPrecip
						curHrPrecip = float(row['precip_accum_since_local_midnight_set_1'])

				else:
					hourlyPrecip = 0.0
					if float(row['precip_accum_since_local_midnight_set_1']) < curHrPrecip:
						prevHrPrecip = 0.0
						curHrPrecip = float(row['precip_accum_since_local_midnight_set_1'])
						totalYearlyPrecip += curHrPrecip
					else:
						prevHrPrecip = curHrPrecip
						curHrPrecip = float(row['precip_accum_since_local_midnight_set_1'])				
								

			with open (rowsAll[0],'a',newline='') as lwcfile:
				#print (str(curHrPrecip))
				rowsAll.extend(["P:"+str(round(totalYearlyPrecip,5))])
				#rowsAll.extend(["PrevHr:" + str(prevHrPrecip)])
				#rowsAll.extend(["CurHr:"+ str(curHrPrecip)])
				#rowsAll.extend(["Prev-Cur:"+ str(hourlyPrecip)])
				lwcWriter = csv.writer(lwcfile, delimiter=' ')
				rowsAll[0] = str(lineNumber)
				lineNumber += 1
				lwcWriter.writerow(rowsAll)

		
			 
		