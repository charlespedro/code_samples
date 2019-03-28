# -*- coding: utf-8 -*-

import numpy as np
import datetime
import pandas as pd
import re

# these are optional, depending on your screen/preference
pd.set_option('display.width', 1900)
pd.set_option('display.max_columns', 12)

# read in files
visit = pd.read_csv('visit.csv')
visit_diag = pd.read_csv('visit_diagnosis.csv')
dept = pd.read_csv('department.csv')
diag = pd.read_csv('diagnosis.csv')
medic = pd.read_csv('medication_order.csv')

# start script output
print('Today\'s date is:', datetime.date.today(), '\n')

print('{0:<32s} {1:8d}'.format('Total visit table rows:', visit['VISIT_KEY'].count()), '\n')


##### Part 1, assembling cohort

# start with just the necessary fields
visit_1 = visit[['VISIT_KEY','PAT_KEY','DEPT_KEY','DICT_ENC_TYPE_KEY','HOSP_ADMIT_DT','AGE']]

## 1. hospital encounter - DICT_ENC_TYPE_KEY=83
enc = visit_1[visit_1['DICT_ENC_TYPE_KEY']==83]
print('{0:<32s} {1:8d}'.format('Hospital encounters:', enc['VISIT_KEY'].count()), '\n')

## 2. date of encounter - after 8/1/2014
enc_dt = enc[enc['HOSP_ADMIT_DT']>'2014-08-01']
print('{0:<32s} {1:8d}'.format('Encounters after Aug 8, 2014:', enc_dt['VISIT_KEY'].count()), '\n')

## 3. age between 1 and 18

# see a histogram of the ages
# enc_dt.hist(column='AGE', bins=20)

enc_age = enc_dt[(enc_dt['AGE']>=1) & (enc_dt['AGE']<=18)]
print('{0:<32s} {1:8d}'.format('Ages 1-18:', enc_age['PAT_KEY'].count()), '\n')

## 4. ED diagnosis

# merge visit cohort and visit diagnosis dataframes
enc_m1 = pd.merge(enc_age, visit_diag, on=['VISIT_KEY','PAT_KEY'])

# filter on 313 and 314
enc_m1_ed = enc_m1[enc_m1['DICT_DX_STS_KEY'].isin([313, 314])]
print('{0:<32s} {1:8d}'.format('ED primary and secondary:', enc_m1_ed['VISIT_KEY'].count()), '\n')

# drop unused fields, remove duplicates
enc_m1_ed = enc_m1_ed[['VISIT_KEY', 'PAT_KEY','AGE','DEPT_KEY','HOSP_ADMIT_DT','DX_KEY']]
enc_m1_ed.drop_duplicates(inplace=True)

icd9_list = ('995.0', 
'995.3', 
'995.6', 
'995.60', 
'995.61', 
'995.62', 
'995.63', 
'995.64', 
'995.65', 
'995.66', 
'995.67',
'995.68', 
'995.69', 
'995.7', 
'999.4', 
'999.41', 
'999.42', 
'999.49')

enc_m2 = pd.merge(enc_m1_ed, diag, on='DX_KEY')
enc_m2_icd9 = enc_m2[enc_m2['ICD9_CD'].isin(icd9_list)]

enc_m2_icd9a = enc_m2_icd9.drop_duplicates()
print('{0:<32s} {1:8d}'.format('In ICD9_CD list:', enc_m2_icd9a['VISIT_KEY'].count()), '\n')

## 5. not urgent care 
enc_m3 = pd.merge(enc_m2_icd9a, dept, on='DEPT_KEY')
enc_m3_noturg = enc_m3[~enc_m3['DEPT_NM'].str.contains('URGENT', na=False)]
print('{0:<32s} {1:8d}'.format('Not urgent care:', enc_m3_noturg['VISIT_KEY'].count()), '\n')

# drop unused fields 
enc_m3_noturg = enc_m3_noturg[['VISIT_KEY', 'PAT_KEY','AGE','DEPT_KEY','HOSP_ADMIT_DT',
    'DX_NM']]


##### Part 2, add new fields

## 1. diagnosis of Anaphylaxis

enc_anaph = enc_m3_noturg
enc_anaph['ANAPH_DX_IND'] = np.where(enc_anaph['DX_NM'].str.contains('anaphylaxis',
         flags=re.IGNORECASE, regex=True, na=False)==True, 1, 0)

enc_anaph.drop_duplicates(inplace=True)
print('{0:<32s} {1:8d}'.format('Cases of anaphylaxis:', 
      enc_anaph[enc_anaph['ANAPH_DX_IND']==1]['VISIT_KEY'].count()), '\n')



## 2. Medication is Epinephrine

# first, get any rows from medic dataframe that contain epinephrine
medic_epi = medic.loc[medic['MED_ORD_NM'].str.contains('epinephrine', flags=re.IGNORECASE, regex=True, 
                    na=False)][['VISIT_KEY','PAT_KEY','MED_ORD_NM']].copy()

# add new column, set all to 1
medic_epi['EPI_ORDER_IND'] = 1

# join original DF with new medic DF
medic_epi_m1 = pd.merge(enc_anaph, medic_epi, how='left', on=['VISIT_KEY','PAT_KEY'])
medic_epi_m1.EPI_ORDER_IND.fillna(0, inplace=True)
medic_epi_m1['EPI_ORDER_IND'] = medic_epi_m1.EPI_ORDER_IND.astype('int')

# drop columns again
enc_epi = medic_epi_m1[['PAT_KEY','VISIT_KEY','HOSP_ADMIT_DT','AGE','ANAPH_DX_IND','EPI_ORDER_IND']]
enc_epi_2 = enc_epi.drop_duplicates()

print('{0:<32s} {1:8d}'.format('Was given Epinephrine:', 
      enc_epi_2[enc_epi_2['EPI_ORDER_IND']==1]['VISIT_KEY'].count()), '\n')

## 3-5. Follow-up; 
#
# It takes two merges and dataframe transformations to handle cases with more than one
# patient/visit and also more than one outpatient visit. Need these steps to match only the most 
# recent hospital encounter and only the first outpatient visit.

# first, get list of all outpatients from original visit table
outpat = visit[visit['DICT_ENC_TYPE_KEY']==108][['PAT_KEY','APPT_CHECKIN_DT']]
outpat_m1 = pd.merge(enc_epi_2, outpat, on=['PAT_KEY'])

# change to datetime objects
outpat_2 = outpat_m1.copy()
outpat_2['HOSP_ADMIT_DT'] = pd.to_datetime(outpat_2['HOSP_ADMIT_DT'], yearfirst=True)
outpat_2['APPT_CHECKIN_DT'] = pd.to_datetime(outpat_2['APPT_CHECKIN_DT'], yearfirst=True)

# Find time delta; the 'd5' column is a temporary placeholder
outpat_3 = outpat_2.copy()
outpat_3['d5'] = (outpat_3['APPT_CHECKIN_DT'].dt.date - outpat_3['HOSP_ADMIT_DT'].dt.date).dt.days

outpat_4 = outpat_3.groupby('PAT_KEY', as_index=False)[['d5','APPT_CHECKIN_DT']].min()
outpat_m4 = pd.merge(enc_epi_2, outpat_4, on='PAT_KEY', how='left') 

# after the above groupby/merge, need to add the date columns back again, change to datetime objects
outpat_5 = outpat_m4.copy()
outpat_5['HOSP_ADMIT_DT'] = pd.to_datetime(outpat_5['HOSP_ADMIT_DT'], yearfirst=True)
outpat_5['APPT_CHECKIN_DT'] = pd.to_datetime(outpat_5['APPT_CHECKIN_DT'], yearfirst=True)

# d6 is another temporary placeholder
outpat_5['d6'] = (outpat_5['APPT_CHECKIN_DT'].dt.date - outpat_5['HOSP_ADMIT_DT'].dt.date).dt.days        

# function to insert blank values for DAYS_TO_FOLLOW_UP
def filter_days(d5, d6):
    if d5 == d6 and d6 < 8 and d6 >= 0:    
        return d6
    else:
        return ''

outpat_6 = outpat_5.copy()
outpat_6['DAYS_TO_FOLLOW_UP'] = outpat_6.apply(lambda row : filter_days(row['d5'], row['d6']), axis=1)

outpat_6.loc[outpat_6['DAYS_TO_FOLLOW_UP'] != '', 'FOLLOW_UP_DATE'] = outpat_6['APPT_CHECKIN_DT']

outpat_6.drop(columns=['d5','d6', 'APPT_CHECKIN_DT'], inplace=True)
outpat_6.FOLLOW_UP_DATE.fillna('', inplace=True)
outpat_6['FOLLOW_UP_IND'] = np.where(outpat_6.DAYS_TO_FOLLOW_UP=='', 0, 1)

# re-order columns to produce final output
df_final = outpat_6[['PAT_KEY','VISIT_KEY','HOSP_ADMIT_DT','AGE','ANAPH_DX_IND','EPI_ORDER_IND',
                      'FOLLOW_UP_IND','FOLLOW_UP_DATE','DAYS_TO_FOLLOW_UP']]

df_final.sort_values(by=['PAT_KEY', 'VISIT_KEY'], inplace=True)

print('{0:<32s} {1:8d}'.format('Outpatient count:', df_final[df_final['FOLLOW_UP_IND']==1]['VISIT_KEY'].count()), '\n')
print('{0:<32s} {1:8d}'.format('Final row count:', df_final['VISIT_KEY'].count()), '\n')

# write output to file
df_final.to_csv(r'C:\Users\england\OneDrive\career\CHOP\final_output.csv', index=False)
