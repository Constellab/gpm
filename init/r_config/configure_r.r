
# Install language service for extension (in R command)
install.packages("languageserver")

print('Configuring for jupyter notebook')
# Config for jupyter notebook
install.packages('IRkernel')

# to register the kernel in the current R installation
# to enable R in jupyter notebook
IRkernel::installspec()  