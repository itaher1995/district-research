# District Dashboard FAQ

If you've been brought here, it means your curious about how/why something is the way it is on the district dashboard.

### Q: Why are some of the percentages of race off between **My Congressional District** (the Census source) and the district dashboard?

A: We report the percent of individuals of that race alone. We also report based on ethnicity. In other words, Percent White will reflect the percent of the population that is only white and not hispanic. Therefore, you'll generally see that **My Congressional District** will report slightly higher percentages than our report.

### Q: What does Democrat/Republican (x) mean?

A: In certain states, the general election can feature more than one member of the party in the general election. This is popular in states like California, where it's possible to have two Democrats in the genral election.

### Q: I checked district dashboard data against NYT/Ballotpedia and found some discrepancies in vote cast numbers, what gives?

A: Before you raise concern please check against the Secretary of State or Board of Elections for the state in which you've found the discrepancy. There are certain situations where news outlets may report unofficial statistics because they stopped counting or the race had been called. We've found that our data can be validated against official records for the state. The exception are house races in 2020. For 2020, we gathered our data from USA Today and Politico.

### Q: why does a district map looks slightly different than the official Congressional District boundaries?

A: The maps are generated using a list of ZCTAs that are within a given Congressional District. Congressional Districts may constitute only part of a ZCTA; however, because we can't plot part of a ZCTA, we plot it in its entireity. ZCTA stands for Zip Code Tabulation Area. It's the census' equivalent to a postal zip code, although it's not a 1:1 mapping.

### Q: How is Voter Turnout Percentage calculated

A: Because of the lack of historical data on the voting population in a district, we use the 2019 estimate for Voting Age Population that are citizens.

### Q: The dashboard is taking a long time to load. What do I do?

A: The web server we are using to host our application is an open source application that several other applications use. Sometimes there may longer than expected loading times because of that or latency that happens because of Colab. While I haven't seen unbearable load times, if you find that its taking too long to load, please notify Ibi Taher and come back at some other time.

### Q: A part of the dashboard failed to load. What do I do?

A: Refresh the dashboard. It should load. This happens very rarely. If not contact Ibi Taher.

## Q: How is the racial diversity index calculated

A: The index is calculated using shannon's entropy. It is a measure of randomness.