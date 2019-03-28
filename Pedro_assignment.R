# R script for three-part assignment
# created by Charles Pedro
# 2/3/2019

setwd("C:/Users/england/OneDrive/career/NASDAQ")

#load packages you'll need
library(RSQLite)
sqlite <- dbDriver("SQLite")

# open database
nqdb <- dbConnect(sqlite, "nqdb3/nqdb3.db")

dbListTables(nqdb)
dbListFields(nqdb, "trds")
dbListFields(nqdb, "qts")

# quick data review
msft <- dbGetQuery(nqdb, statement = "select * from trds where Symbol='MSFT' limit 20")
msft

all_trade <- dbGetQuery(nqdb, statement = "select * from trds")

head(all_trade)
tail(all_trade)
summary(all_trade)

unique(all_trade$Symbol)
unique(all_trade$SaleCondition)
unique(all_trade$RefDate)



######## part 1 ########

# it looks like this SQLite package doesn't do regexp, so I need to list out 
# all the sale conditions 

all_sym <- dbGetQuery(nqdb, statement = 
"with open as
(select RefDate, Symbol, Price OpeningPrice from trds where SaleCondition like '@O%' and Pid = 'Q'),
min_max_avg as
(select Symbol, min(Price) MinPrice, max(Price) MaxPrice, avg(Price) AvgPrice,
sum(Quantity*Price)/sum(Quantity) VWAP
from trds where 
SaleCondition not like '%C%' 
and SaleCondition not like '%G%'
and SaleCondition not like '%I%'
and SaleCondition not like '%H%'
and SaleCondition not like '%M%'
and SaleCondition not like '%N%'
and SaleCondition not like '%P%'
and SaleCondition not like '%Q%'
and SaleCondition not like '%R%'
and SaleCondition not like '%T%'
and SaleCondition not like '%U%'
and SaleCondition not like '%V%'
and SaleCondition not like '%W%'
and SaleCondition not like '%Z%'
and SaleCondition not like '%4%'
and SaleCondition not like '%7%'
group by Symbol),
close as
(select Symbol, Price ClosingPrice from trds where SaleCondition like '@6%' and Pid = 'Q'
group by Symbol),
trades_shares as
(select Symbol, count(*) Trades, sum(Quantity) Shares
from trds where  
SaleCondition not like '%M%'
and SaleCondition not like '%Q%'
and SaleCondition not like '%9%'
group by Symbol)
select o.RefDate, o.Symbol, OpeningPrice, ClosingPrice, MinPrice, MaxPrice, AvgPrice, 
VWAP, Trades, Shares, (MaxPrice-MinPrice)/ClosingPrice PctRange
from open o join close c on o.Symbol = c.Symbol
join min_max_avg m on o.Symbol = m.Symbol
join trades_shares ts on o.Symbol = ts.Symbol
group by o.Symbol
order by PctRange desc")

# print the output; looks good
all_sym

# create output file
write.csv(all_sym, file="DaySummary_v02.csv", row.names = FALSE)



######## part 2 ########

five_min <- dbGetQuery(nqdb, statement = "select RefDate, Symbol,
cast(Timestamp/3e5 as int) TimeBucket,
time(cast(Timestamp/3e5 as int)*300, 'unixepoch') StartTime,
max(Price) MaxPrice,
min(Price) MinPrice,
avg(Price) AvgPrice,
case when Timestamp = max(Timestamp)
then Price
end as LastPrice
from trds where TimeStamp between 34200000 and 57600000 and
SaleCondition not like '%C%' 
and SaleCondition not like '%G%'
and SaleCondition not like '%I%'
and SaleCondition not like '%H%'
and SaleCondition not like '%M%'
and SaleCondition not like '%N%'
and SaleCondition not like '%P%'
and SaleCondition not like '%Q%'
and SaleCondition not like '%R%'
and SaleCondition not like '%T%'
and SaleCondition not like '%U%'
and SaleCondition not like '%V%'
and SaleCondition not like '%W%'
and SaleCondition not like '%Z%'
and SaleCondition not like '%4%'
and SaleCondition not like '%7%'
group by TimeBucket, Symbol
order by Symbol, TimeBucket")


# check a few
head(five_min, n=30)
subset(five_min, subset = Symbol=='AMZN')
subset(five_min, subset = TimeBucket=='191')

# create output file
write.csv(five_min, file="FiveMins_v02.csv", row.names = FALSE)



######## part 3 ########

# first, get quotes into a data frame
qts <- dbGetQuery(nqdb, statement = "select RefDate, Symbol, Timestamp,
BidPrice, AskPrice from qts where TimeStamp between 34200000 and 57600000")

# add the columns that appear in trade table
qts <- cbind(qts, 'Price'=NA, 'Quantity'=NA, 'Pid'=NA)
head(qts)

# do the same for trades 
trd <- dbGetQuery(nqdb, statement = "select RefDate, Symbol, Timestamp,
Price, Quantity, Pid
from trds where Symbol = 'MSFT' and TimeStamp between 34200000 and 57600000 and
SaleCondition not like '%C%' 
and SaleCondition not like '%G%'
and SaleCondition not like '%I%'
and SaleCondition not like '%H%'
and SaleCondition not like '%M%'
and SaleCondition not like '%N%'
and SaleCondition not like '%P%'
and SaleCondition not like '%Q%'
and SaleCondition not like '%R%'
and SaleCondition not like '%T%'
and SaleCondition not like '%U%'
and SaleCondition not like '%V%'
and SaleCondition not like '%W%'
and SaleCondition not like '%Z%'
and SaleCondition not like '%4%'
and SaleCondition not like '%7%'")

head(trd)

# add bid and ask columns
trd <- cbind(trd, 'BidPrice'=NA, 'AskPrice'=NA)

head(trd)
nrow(qts)
nrow(trd)

# combine them into one data frame and sort by timestamp
qts_trd <- rbind(qts, trd)
qts_trd <- qts_trd[order(qts_trd$Timestamp), c(1:8)]

nrow(qts_trd)

head(qts_trd, n=30)

qts_trd_2 <- qts_trd
head(qts_trd_2, n=30)

# setting these initial values because the first rows are trades, not quotes
# after the first few iterations, then set the bid and ask until the next trade, 
# and assign the new values
bid = 46.87
ask = 47.0

# iterate over the data frame
# set the bid and ask values when price is NA, and assign them for each trade when bid is NA
# this takes about a minute to run

for (x in 1:nrow(qts_trd_2)) {
  if (is.na(qts_trd_2$Price[x])) {
    bid = qts_trd_2$BidPrice[x]
    ask = qts_trd_2$AskPrice[x]    
  }
  if (is.na(qts_trd_2$BidPrice[x])) {
    qts_trd_2$BidPrice[x] = bid
    qts_trd_2$AskPrice[x] = ask    
  }  
}


# looks good
head(qts_trd_2, n=30)
nrow(qts_trd_2)

# remove the quotes (where Price is NA)
qts_trd_2 <- subset(qts_trd_2, !is.na(Price))
head(qts_trd_2, n=30)

# get just a selection of rows
qts_trd_final <- qts_trd_2[c(1:100, 100000:100050),]

nrow(qts_trd_final)
tail(qts_trd_final, n=30)

# write output file that matches the one provided
write.csv(qts_trd_final, file="TradesAndQuotes_v02.csv", row.names = FALSE)


#### finally, add column to calculate effective spread 
#### I'll use the original data with all rows
qts_trd_spread <- cbind(qts_trd_2, 'Spread'=NA)
head(qts_trd_spread)
nrow(qts_trd_spread)

for (x in 1:nrow(qts_trd_spread)) {
  # bam = bid-ask midpoint
  bam = (qts_trd_spread$AskPrice[x] + qts_trd_spread$BidPrice[x])/2.0
  # calculate the spread
  qts_trd_spread$Spread[x] = abs(qts_trd_spread$Price[x] - bam)/bam
}

head(qts_trd_spread, n=30)
tail(qts_trd_spread, n=30)

# calculate the volume-weighted average spread for the day
day_spread <- sum(qts_trd_spread$Quantity*qts_trd_spread$Spread)/sum(qts_trd_spread$Quantity)
day_spread <- round(day_spread*10000, 4)

# I get 0.9186
print(paste("The volume-weighted average effective spread is", day_spread,"bps"))

# disconnect from database when finished for the day
dbDisconnect(nqdb)

