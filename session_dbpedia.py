import spotlight

sample_txt = "President Obama on Monday will call for a new minimum tax rate for individuals making more than $1 " \
             "million a year to ensure that they pay at least the same percentage of their earnings as other " \
             "taxpayers, according to administration officials."

a = spotlight.annotate('http://model.dbpedia-spotlight.org/en/annotate', sample_txt)

print(a)

