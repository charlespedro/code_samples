#!/usr/bin/perl use strict;

# Author:  Chuck Pedro
# Date:  May 22, 2007
#
# This program is written to parse persist log files, to be more readable.
# There are four options; with  heartbeats, without heartbeats, and you can tail the log file,
# or send the output to a separate file.
#
# Run fixo by itself and it will tail the log. Run fixo with an argument, such as "fixo out", and
# it will send the output to the file "out".
#
# fixo will ask you if you want heartbeats or not. Hit "y" for yes, or Enter for no.
# fixo will then ask the name of the log file to be parsed.

# chdir ("/home/etssec/bear_apps/var/persist");
my $file;
my $date = `date +"%Y%m%d"`;
my %tag;
my %open_tag;
my $SOH = "\x01";

&load_tag;
chomp $date;

if ($ARGV[O] =~ m/xo/) {
open OUTPUT, ">$ARGV[0]";
}

print "Do you want hearbeat messages?\n (hit \"y\",  or ENTER key for no.)";
chomp(my $heart = <STDIN>);

print "Which file? ";
chomp($file = <STDIN>);

if ($ARGV[0])
{
open (INPUT, "<$file") || die "Could not read $file in:  $!\n";
select OUTPUT;
} else {
open (INPUT, "tail -f $file!") || die "Could not read $file in:  $!\n";
}

while (<INPUT>)
{
	if (($heart eq "y") && (m/^M/))
	{
		my @pipe = split '\|', $_;
		my @input = split /$SOH/, $pipe[7];
		print "Timestamp";
		printf "%46s", "$pipe[5]\n";
		for (@input)
		{
			my $b = &find_tag($_);
			my @field = split '=', $_;
			unless (("$field[0]" eq "9") || ("$field[0]" eq "10"))
			{
				printf "%-33s", "$b";
				printf "%-5s %-5s\n", "$field[0]","$field[1]";
			}
		}
	print "\n";
	} elsif ($_ =~ m/35\=[A-Z,1-9]/)
	{
		my @pipe = split '\|', $_;
		my @input = split /$SOH/,  $pipe[7];
		print "Timestamp";
		printf "%46s", "$pipe[5]\n";
		for (@input)
		{
			my $b = &find_tag($_);
			my @field = split '=', $_;
			unless (("$field[0]" eq "9") || ("$field[0]" eq "10"))
			{
				printf "%-33s", "$b";
				printf "%-5s %-5s\n",  "$field[O]","$field[1]";
			}
		}
	print "\n";
	}
}


sub find_tag
{
my $a = "";
	foreach my $key (keys %tag)
	{
		if ("$_" eq "$key")
		{
			$a = $tag{$key};
		}
	}
	if ("$a" eq "")
	{
		my $c = (split '=', $_)[0];
		foreach my $key (keys %open_tag)
		{
			if ("$c" eq "$key")
			{
				$a = $open_tag{$key};
			}
		}
	}
	$a;
}



sub load_tag {
%tag= (
"20=0" => "New",
"20=1" => "Trade Cancel", 
"20=2" => "Trade Correction",
"20=3" => "Trade Status", 
"35=0" => "Heartbeat", 
"35=1" => "Test Request",
"35=2" => "Resend Request",
"35=4" => "Seq Reset", 
"35=5" => "Logout", 
"35=6" => "IOI",
"35=8" => "Exec Report", 
"35=A" => "Logon", 
"35=D" => "New Order", 
"35=E" => "List Order", 
"35=F" => "CANCEL", 
"35=G" => "REPLACE",
"35=Q" => "Don't Know Trade",
"39=0" => "New Order ACK", 
"39=1" => "Partial Fill",
"39=2" => "Total Fill", 
"39=4" => "CANCELED", 
"39=5" => "REPLACED", 
"39=6" => "Pending Cancel", 
"39=8" => "REJECTED", 
"39=A" => "Pending New", 
"39=E" => "Pending Replace", 
"40=1" => "MKT Order",
"40=2" => "Limit Order",
"40=3" => "Stop Order", 
"40=4" => "Stop Limit", 
"40=5" => "Mkt on Close", 
"40=6" => "With or Without", 
"43=Y" => "Poss Dup flag", 
"54=1" => "Buy",
"54=2" => "Sell",
"54=3" => "Buy Minus", 
"54=4" => "Sell Plus", 
"54=5" => "Sell Short",
"54=6" => "Sell Short Exempt", 
"59=0" => "DAY",
"59=1" => "GTC",
"59=2" => "At the Open", 
"59=3" => "IOC",
"59=4" => "FOK",
"59=5" => "GTX", 
"59=6" => "GTD",
"63=0" => "Settlement - Regular",
"63=1" => "Settlement - Cash", 
"63=2" => "Settlement - Next Day", 
"123=Y" => "Gap Fill message",
);

%open_tag  = ( 
"1" => "Account", 
"6" => "Avg Price",
"11" => "Client Order ID", 
"14" => "CumQty",
"15" => "Currency", 
"16" => "EndSeqNo",
"17" => "Execution ID", 
"18" => "Exec Instruction",
"21" => "Handling Instruction", 
"30" => "Last Market",
"31" => "Fill Price", 
"32" => "Fill Shares", 
"34" => "Seq Number",
"36" => "New Seq Num",
"37" => "Order ID",
"38" => "Total Order Qty", 
"41" => "Old Client OrdlD", 
"42" => "Originating Time", 
"44" => "Limit price",
"47" => "Rule BOA",
"48" => "Security Identifier", 
"49" => "Sender Compld", 
"50" => "Sender Subld",
"52" => "Sending Time", 
"55" => "Symbol",
"56" => "Target Compld", 
"57" => "Target Subld", 
"58" => "Free Text",
"60" => "Transact Time", 
"62" => "Valid Until Time", 
"65" => "Symbol Suffix", 
"76" => "Executing Broker", 
"84" => "Cancel Qty",
"99" => "Stop Price", 
"100" => "Destination",
"102" => "CxlReject Reason",
"103" => "OrderReject Reason", 
"109" => "Clientld",
"115" => "OnBehalfOfCompld", 
"116" => "OnBehalfOfSubld", 
"126" => "Expire Time",
"128" => "DeliverToCompld", 
"129" => "DeliverToSubld", 
"150" => "Execution Type", 
"151" => "Leaves QTY",
"167" => "Security Type",
"200" => "MaturityMonthYear", 
"204" => "CustomerOrFirm", 
"205" => "MaturityDay",
"207" => "SecurityExchange",
"432" => "Expire Date"
);
}

close INPUT;
close OUTPUT;

if ($ARGV[0])
{
	system("vi $ARGV[0]");
}

if ("$ARGV[0]" =~ "xo")
{
	unlink "$ARGV[0]" or die "Could not remove $ARGV[0]!\n";
}
