# Chuck Pedro
# Final Python and web project
# See accompanying web notes for more information about this script

import requests
import json
import csv
import os

# set these now to be used later
main_dict = {}

max_gdp = 0
max_sanitation = 0
max_mortality = 0
max_metric = 0

min_gdp = 1000000000000000
min_sanitation = 1000
min_mortality = 0
min_metric = 1000

stats_max = {}
stats_min = {}
stats_avg = {}

# remove these files if they exists; will write to it later
try:
        os.remove('final_stats.csv')
        os.remove('final_output.csv')
except OSError:
        pass


# First, find out which countries are low income (LIC) or low middle income (LMC)
print '\nGetting list of countries to query...\n'
print '\nLIC = Low Income'
print 'LMC = Lower Middle Income\n'

endpoint = 'http://api.worldbank.org/countries?per_page=300&format=json'
response = requests.get(endpoint)
data = response.json()

country_count = 0
for result in data[1]:
    if result['incomeLevel']['id'] in ('LIC', 'LMC'):
        # excluding South Sudan and Kosovo
        if result['iso2Code'] not in ['SS', 'XK']:
            # remove comma in country names because it messes up csv
            no_comma = result['name'].replace(',','')
            print ("%s %-29s %-10s" % (result['iso2Code'], result['name'], result['incomeLevel']['id']))
            # define dictionary to be used throughout this script
            main_dict[result['iso2Code']] = [no_comma,0,0,0,0,0,0]
            country_count += 1



# define function to make aid numbers more readable because it is returned in in dollars
def conversion(total):
        if total > 1000000000:
                converted_aid = round(total/1000000000, 2)
                converted_aid = str(converted_aid) + 'b'
        elif total > 1000000:
                converted_aid = round(total/1000000, 2)
                converted_aid = str(converted_aid) + 'm'
        else:
            converted_aid = total
        return converted_aid


print '\n', country_count, 'country names and codes were retrieved\n'
print 'Making API calls...\n'


#
# API Calls
#

# Net official development assistance and official aid received (current US$)
endpoint = 'http://api.worldbank.org/countries/indicators/DT.ODA.ALLD.CD?per_page=3000&date=2001:2010&format=json'
      
response = requests.get(endpoint)
data = response.json()

for result in data[1]:
        year = result['date']
        aid = result['value']
        country = result['country']['value']
        id = result['country']['id']
        if id in main_dict.keys():
                if str(aid) != 'None':
                        main_dict[id][1] += float(aid)


# GDP per capita growth (annual %)
endpoint = 'http://api.worldbank.org/countries/indicators/NY.GDP.PCAP.KD.ZG?per_page=3000&date=2001:2010&format=json'
response = requests.get(endpoint)
data = response.json()

for result in data[1]:
        year = result['date']
        growth = result['value']
        id = result['country']['id']
        if id in main_dict.keys():
            if str(growth) != 'None':
                main_dict[id][2] += float(growth)


# Improved sanitation facilities (% of population with access)
endpoint = 'http://api.worldbank.org/countries/indicators/SH.STA.ACSN?per_page=3000&date=2001:2010&format=json'
response = requests.get(endpoint)
data = response.json()

for result in data[1]:
        year = result['date']
        val = result['value']
        id = result['country']['id']
        if id in main_dict.keys():
            if year == '2010':
                if str(val) != 'None':
                    main_dict[id][3] += float(val)
            elif year == '2001':
                if str(val) != 'None':
                    main_dict[id][4] += float(val)


# Mortality rate, under-5 (per 1,000 live births)
endpoint = 'http://api.worldbank.org/countries/indicators/SH.DYN.MORT?per_page=3000&date=2001:2010&format=json'
response = requests.get(endpoint)
data = response.json()

for result in data[1]:
        year = result['date']
        val = result['value']
        id = result['country']['id']
        if id in main_dict.keys():
            if year == '2010':
                if str(val) != 'None':
                    main_dict[id][5] += float(val)
            elif year == '2001':
                if str(val) != 'None':
                    main_dict[id][6] += float(val)

#
# Output to screen
#

print """
1 = Country code
2 = Country name
3 = Total official development assistance (ODA) and official aid received (current USD), 2001-2010
4 = Simple average of column 1; average ODA per year, 2001-2010
5 = Simple average of GDP per capita growth per year, 2001-2010
6 = Change in improved sanitation facilities (% of population with access) between 2001 and 2010
7 = Change in mortality rate, children under 5yo (per 1,000 live births) between 2001 and 2010
8 = Computed metric to evaluate the effectiveness of aid based on these data (higher number is better)

"""
print ("%-4s %-25s %-8s %-8s %-8s %-8s %-8s %s" % ('1', '2', '3', '4', '5', '6', '7', '8'))


# loop through main_dict to get or calculate values
for j in sorted(main_dict.keys()):
    converted_aid = conversion(main_dict[j][1])
    avg_aid = conversion(main_dict[j][1]/10)
    avg_gdp = round(main_dict[j][2]/10, 2)
    # finding the percentage difference between 2010 and 2001
    change_sanitation = round((main_dict[j][3] - main_dict[j][4])/main_dict[j][4]*100, 2)
    change_mortality = round((main_dict[j][5]-main_dict[j][6])/main_dict[j][6]*100, 2)
    # calculating the aid effectiveness metric
    if main_dict[j][1] > 0:
        metric = (-pow(main_dict[j][1]/100000000, .5) + main_dict[j][2]/4 + change_sanitation*.5 - \
                  change_mortality*.3 + 80)*.2
        metric = round(metric, 1)
    else:
        metric = 'N/A'
    # Find max and min values
    # find max value of total aid
    if main_dict[j][1] == max(v[1] for v in main_dict.values()):
        stats_max['aid'] = [main_dict[j][0], main_dict[j][1]]
    # find max value of average GDP per capita
    if avg_gdp > max_gdp:
        max_gdp = avg_gdp
        stats_max['gdp'] = [main_dict[j][0], avg_gdp]
    # find max value of change in sanitation access
    if change_sanitation > max_sanitation:
        max_sanitation = change_sanitation
        stats_max['san'] = [main_dict[j][0], change_sanitation]
    # find max value of change in mortality rate
    if change_mortality < max_mortality:
        max_mortality = change_mortality
        stats_max['mortality'] = [main_dict[j][0], change_mortality]                        
    # find max value of metric
    if metric > max_metric:
        max_metric = metric
        stats_max['metric'] = [main_dict[j][0], metric]
    # Min values
    # find min value of total aid
    if main_dict[j][1] == min(v[1] for v in main_dict.values()):
        stats_min['aid'] = [main_dict[j][0], main_dict[j][1]]
    # find min value of average GDP per capita
    if avg_gdp < min_gdp:
        min_gdp = avg_gdp
        stats_min['gdp'] = [main_dict[j][0], avg_gdp]
    # find min value of change in sanitation access
    if change_sanitation < min_sanitation:
        min_sanitation = change_sanitation
        stats_min['san'] = [main_dict[j][0], change_sanitation]
    # find min value of change in mortality rate
    if change_mortality > min_mortality:
        min_mortality = change_mortality
        stats_min['mortality'] = [main_dict[j][0], change_mortality]
    # find min value of metric
    if metric < min_metric:
        min_metric = metric
        stats_min['metric'] = [main_dict[j][0], metric]
    stats_avg[j] = [change_sanitation, change_mortality, metric]

    # print to screen
    print ("%-4s %-25s %-8s %-8s %-8s %-8s %-8s %s" % (j, main_dict[j][0], converted_aid, avg_aid,
           avg_gdp, change_sanitation, change_mortality, metric))
    # print to csv file
    with open('final_output.csv', 'ab') as output:
            writer = csv.writer(output)
            writer.writerow([j, main_dict[j][0], converted_aid, avg_aid,
           avg_gdp, change_sanitation, change_mortality, metric])

#
# Print summary statistics
#


print '\n\nStatistics\n'

print ("%-17s %-15s %-22s %-15s %-15s %-9s" % (' ', 'MAX VALUE', 'MAX COUNTRY', 'MIN VALUE', 'MIN COUNTRY', 'AVERAGE'))
print ("%-17s %-15s %-22s %-15s %-15s %-9s" % ('Total aid (USD):', conversion(stats_max['aid'][1]), stats_max['aid'][0],
       conversion(stats_min['aid'][1]), stats_min['aid'][0],
       conversion(sum(v[1] for v in main_dict.values())/country_count)))

print ("%-17s %-15s %-22s %-15s %-15s %-9s" % ('GDP per cap (%):', stats_max['gdp'][1], stats_max['gdp'][0],
       stats_min['gdp'][1], stats_min['gdp'][0],
        round(sum(v[2] for v in main_dict.values())/(country_count*10), 2)))

print ("%-17s %-15s %-22s %-15s %-15s %-9s" % ('Sanitation (%):', stats_max['san'][1], stats_max['san'][0],
       stats_min['san'][1], stats_min['san'][0],
        round(sum(v[0] for v in stats_avg.values())/country_count, 2)))

print ("%-17s %-15s %-22s %-15s %-15s %-9s" % ('Mortality (%):', stats_max['mortality'][1], stats_max['mortality'][0],
       stats_min['mortality'][1], stats_min['mortality'][0],
        round(sum(v[1] for v in stats_avg.values())/country_count, 2)))

print ("%-17s %-15s %-22s %-15s %-15s %-9s" % ('Metric:', stats_max['metric'][1], stats_max['metric'][0],
       stats_min['metric'][1], stats_min['metric'][0],
        round(sum(v[2] for v in stats_avg.values())/country_count, 2)))		

with open ('final_stats.csv', 'wb') as stats:
        writer = csv.writer(stats)
        writer.writerow([' ','MAX VALUE','MAX COUNTRY','MIN VALUE','MIN COUNTRY','AVERAGE'])
        writer.writerow(['Total aid (USD):', conversion(stats_max['aid'][1]), stats_max['aid'][0],
            conversion(stats_min['aid'][1]), stats_min['aid'][0],
            conversion(sum(v[1] for v in main_dict.values())/country_count)])
        writer.writerow(['GDP per cap (%):', stats_max['gdp'][1], stats_max['gdp'][0],
       stats_min['gdp'][1], stats_min['gdp'][0],round(sum(v[2] for v in main_dict.values())/(country_count*10), 2)])
        writer.writerow(['Sanitation (%):', stats_max['san'][1], stats_max['san'][0],
       stats_min['san'][1], stats_min['san'][0], round(sum(v[0] for v in stats_avg.values())/country_count, 2)])          
        writer.writerow(['Mortality (%):', stats_max['mortality'][1], stats_max['mortality'][0],
       stats_min['mortality'][1], stats_min['mortality'][0], round(sum(v[1] for v in stats_avg.values())/country_count, 2)])
        writer.writerow(['Metric:', stats_max['metric'][1], stats_max['metric'][0],
                         stats_min['metric'][1], stats_min['metric'][0],
                         round(sum(v[2] for v in stats_avg.values())/country_count, 2)])
	
print '\n'
output.close()
stats.close()


