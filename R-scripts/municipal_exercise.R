# Load required libraries
library(rgdal)
library(spdep)

# Read in the municipalities shapefile
municipals <- readOGR('./Municipals_Finland/Municipals_Finland.shp', encoding="UTF-8")

#Plot the full shapefile
#plot(municipals)

# View column names in the shapefile
#names(municipals)

# Print municipality IDs (KUNTANUMER) and names (KUNTANIMI)
#print(municipals$KUNTANUMER)        
#print(municipals$KUNTANIMI)

print(data.frame(municipals$KUNTANUMER, municipals$KUNTANIMI))

# Select and print municipalities Helsinki and Vantaa
selection <- c("Helsinki","Vantaa")
print(selection)

selected_municipals <- municipals[municipals$KUNTANIMI%in%selection,]

# Plot only the selected municipalities (Helsinki and Vantaa)
#plot(selected_municipals)

# Assign white color to the selected
selected_municipals$COLOR <- "#FFFFFF"

# Print names of selected municipalities
#print(selected_municipals$KUNTANIMI)

# Assign red to the first municipal (Helsinki)
selected_municipals$COLOR[1] <- "#FF0000"

# Plot selected municipalities with assigned colors
#plot(selected_municipals, col= selected_municipals$COLOR)

# Select a larger set of municipalities in the region (including Helsinki, Vantaa, etc.)
selection2 <- c("Hyvink\xe4\xe4","Vihti","Nurmij\xe4rvi","Tuusula","Vantaa","Helsinki","Sipoo","Kerava","J\xe4rvenp\xe4\xe4","Pornainen","M\xe4nts\xe4l\xe4")

selected_municipals2 <- municipals[municipals$KUNTANIMI%in%selection2,]

print(selection2)

# Plot the selected group of municipalities
#plot(selected_municipals2)

selected_municipals2$COLOR <- "lightgrey"
selected_municipals2$COLOR[8] <- "#FF0000"

# Plot selected municipalities with coloring
#plot(selected_municipals2, col = selected_municipals2$COLOR)

# Allow neighbors with no neighbors without errors
set.ZeroPolicyOption(TRUE)

# Create neighbor list based on polygon contiguity (rook’s case, queen=FALSE)
municipals_nb <- poly2nb(selected_municipals2, queen=FALSE)

# Show structure of neighbors list
str(municipals_nb)

# Plot neighbors over municipality centroids (grey lines showing neighbors)
#plot(municipals_nb,coordinates(selected_municipals2),col="grey")

# Extract centroids of the selected municipalities
coordinates(selected_municipals2)

# Convert neighbors list to an adjacency matrix
municipals_adj <- nb2mat(municipals_nb, style="B")

# Convers neighbors list to a normalized adjacency matrix
municipals_adj <- nb2mat(municipals_nb)

# Print adjacency matrix to console
#print(municipals_adj)

# Crime rates assigned to selected municipalities
crimes = c(47.6, 60.90, 44.60, 43.80, 61.40, 29.70, 126.00, 116.30, 75.50, 69.10, 76.00)
selected_municipals2$CRIME <- crimes

# Create spatial weights list object (row-standardized)
mymap_w <- nb2listw(municipals_nb)

# Compute Moran’s I statistic for spatial autocorrelation of crime and print results
mI_norm <- moran.test(selected_municipals2$CRIME, mymap_w, randomisation=TRUE)
print(mI_norm)

# Calculate geographic centers: mean and weighted mean by crime

# Extract centroids of municipalities
municipal_centers <- coordinates(selected_municipals2)

# Calculate mean X and Y of centroids (unweighted mean center)
mean_center_x <- mean(municipal_centers [, 1])
mean_center_y <- mean(municipal_centers [, 2])

# Plot municipalities
plot(selected_municipals2)

# Plot mean center as red point
points(mean_center_x, mean_center_y, col="red", pch=16)

# Calculate weighted mean X and Y by crime rates
weighted_mean_x <- weighted.mean(municipal_centers[, 1], selected_municipals2$CRIME)
weighted_mean_y <- weighted.mean(municipal_centers[, 2], selected_municipals2$CRIME)

# Plot weighted mean center as blue point
points(weighted_mean_x, weighted_mean_y, col="blue", pch =16)
