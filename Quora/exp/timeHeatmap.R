library(ggplot2)

data = read.csv("quora_times.csv")

ggplot(data,aes(x=factor(month), y= factor(year))) +
    geom_tile(stat="bin",aes(fill=..count..)) +
    theme_bw() + scale_fill_gradient(low="white",high="steelblue4") +
    scale_y_discrete(limits=rev(levels(factor(data$year)))) +
    ylab("Year") + xlab("Month")
ggsave('num_docs_heat.pdf')

###########################################################
###########################################################

ggplot(data, aes(x=factor(month))) +
    geom_bar(aes(fill = factor(month))) + theme_bw() +
    facet_grid(year ~ .) + theme(legend.position="bottom") +
    xlab("Month") + ylab("Number of documents")

ggplot(data, aes(x=factor(month))) +
   geom_bar(aes(fill = ..count..)) + theme_bw() +
   scale_fill_gradient(low="white",high="steelblue4") +
   facet_grid(year ~ .) + theme(legend.position="none") +
   xlab("Month") + ylab("Number of documents")
ggsave('num_docs_faceted_bar.pdf')
