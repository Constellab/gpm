
# Install language service for extension (in R command)
install.packages("languageserver", repos = "https://cloud.r-project.org/")

print('Configuring for jupyter notebook')
# Config for jupyter notebook
install.packages('IRkernel', repos = "https://cloud.r-project.org/")

# to register the kernel in the current R installation
# to enable R in jupyter notebook
IRkernel::installspec()  